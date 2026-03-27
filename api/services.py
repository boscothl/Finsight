import os
import json
import re
from datetime import date
from django.core.serializers.json import DjangoJSONEncoder

# Vertex AI Imports
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# Import Models for Agent 1 Data Pipeline
from api.models import Claim, GLTransaction, BudgetPool, ReceiptFile, GLAccount, GLTransactionLine

# --- GCP Configuration ---
PROJECT_ID = "finsight-484914"
LOCATION = "us-central1"

def _init_vertex():
    """Ensure Vertex AI is initialized using the correct project and region."""
    # Note: Assumes GOOGLE_APPLICATION_CREDENTIALS env var is already available in the running environment
    vertexai.init(project=PROJECT_ID, location=LOCATION)

class StyleExtractorService:
    @staticmethod
    def extract_style_from_image(file_data, mime_type="image/jpeg"):
        """
        Multimodal pipeline to extract typography and base colors 
        from a raw PDF or Image into a normalized JSON payload.
        """
        _init_vertex()
        model = GenerativeModel("gemini-2.5-pro")
        
        # Read the file from bytes
        image_part = Part.from_data(file_data, mime_type=mime_type)

        prompt = """
        You are an expert UI/UX and graphical designer. Look at the attached document/image.
        Please extract the styling information to be used as a design system reference for generating reports (Excel, PowerPoint, Word).
        
        Identify the following:
        1. Primary Color (hex code)
        2. Secondary Color (hex code)
        3. Background Color (hex code)
        4. Text Color (hex code)
        5. Primary Font (guess the closest standard font like Arial, Calibri, Times New Roman, etc.)
        6. Title Layout (e.g., Centered, Left-Aligned)
        7. Detailed description of the styling (VERY IMPORTANT)
        
        Respond STRICTLY in pure JSON format:
        {
          "colors": {
            "primary": "",
            "secondary": "",
            "background": "",
            "text": ""
          },
          "fonts": {
            "primary": ""
          },
          "layout": {
            "title_alignment": ""
          },
          "description": "A short prompt-friendly description of the styling vibe."
        }
        """
        
        response = model.generate_content([image_part, prompt])
        
        # Clean response and return loaded dict
        match = re.search(r'```json\n(.*?)```', response.text, re.DOTALL)
        raw_text = match.group(1).strip() if match else response.text.strip()
        
        try:
            return json.loads(raw_text)
        except Exception as e:
            return {"error": "Failed to parse style JSON", "raw": raw_text}

import os
from google.cloud import documentai
from google.cloud import storage
import json

class DocumentAIService:
    @staticmethod
    def extract_receipt(file_data, mime_type="image/jpeg", original_filename="receipt.jpg"):
        """
        Wraps google-cloud-documentai to process receipts.
        Also uploads the raw image to GCS if configured.
        """
        project_id = os.getenv('GCP_PROJECT_ID', '')
        location = os.getenv('DOCAI_LOCATION', 'us')
        processor_id = os.getenv('DOCAI_PROCESSOR_ID', '')
        bucket_name = os.getenv('GS_BUCKET_NAME', '')

        gcs_uri = None

        # 1. Upload to GCS
        if bucket_name:
            try:
                storage_client = storage.Client()
                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob(f"receipts/mobile_uploads/{original_filename}")
                file_data.seek(0)
                blob.upload_from_file(file_data, content_type=mime_type)
                gcs_uri = f"gs://{bucket_name}/{blob.name}"
            except Exception as e:
                print(f"Warning: Failed to upload to GCS - {e}")


        # 2. Extract with Document AI or fallback to Gemini 2.5 Pro
        if not project_id or not processor_id:
            try:
                import vertexai
                from vertexai.generative_models import GenerativeModel, Part
                vertexai.init(project="finsight-484914", location="us-central1")
                model = GenerativeModel("gemini-2.5-pro")
                file_data.seek(0)
                image_part = Part.from_data(file_data.read(), mime_type=mime_type)
                prompt = "Extract receipt details: merchant name, total amount as float, date (YYYY-MM-DD), and a simple category. Return JSON strictly like {'merchant': 'name', 'amount': 123.45, 'date': 'YYYY-MM-DD', 'category': 'Meals'}"
                res = model.generate_content([image_part, prompt])
                import re, json
                match = re.search(r'```json\n(.*?)```', res.text, re.DOTALL)
                raw = match.group(1).strip() if match else res.text.strip()
                data = json.loads(raw)
                return {
                    "merchant": data.get("merchant", "Unknown Merchant"),
                    "date": data.get("date", ""),
                    "amount": float(data.get("amount", 0.0)),
                    "currency": "HKD",
                    "category": data.get("category", "Uncategorized"),
                    "gcs_uri": gcs_uri
                }
            except Exception as e:
                print("Fallback Gemini error:", e)
                return {"merchant": f"Error: {str(e)}", "date": "2026-03-24", "amount": 0.0, "currency": "HKD", "category": "Error"}


        try:
            client = documentai.DocumentProcessorServiceClient()
            name = client.processor_path(project_id, location, processor_id)
            
            # Read file content if not using GCS uri specifically
            file_data.seek(0)
            raw_document = documentai.RawDocument(content=file_data.read(), mime_type=mime_type)
            request = documentai.ProcessRequest(name=name, raw_document=raw_document)
            result = client.process_document(request=request)
            document = result.document

            extracted = {"currency": "HKD", "merchant": "", "amount": 0.0, "date": "", "gcs_uri": gcs_uri}
            
            for entity in document.entities:
                type_ = entity.type_
                value = entity.mention_text
                if type_ == "supplier_name":
                    extracted["merchant"] = value
                elif type_ == "total_amount":
                    # basic clean up
                    num_str = value.replace('$', '').replace(',', '')
                    try:
                        extracted["amount"] = float(num_str)
                    except:
                        pass
                elif type_ == "invoice_date":
                    extracted["date"] = value
                elif type_ == "currency":
                    extracted["currency"] = value

            return extracted

        except Exception as e:
            print(f"Doc AI Error: {e}")
            return {
                "error": str(e),
                "merchant": "Error Parsing",
                "amount": 0.0,
                "gcs_uri": gcs_uri
            }

class ChatbotService:
    @staticmethod
    def generate_response(message, context="employee"):
        """
        Wraps vertexai to handle chat prompts.
        """
        return f"Hello, I am the {context} chatbot. You said: '{message}'. (AI Integration Pending)"

    @staticmethod
    def generate_report_chat_response(session, latest_user_message):
        """
        Handles the conversational flow for Report Generation. 
        It appends previous messages to establish context, checks intent,
        and generates the report if all criteria are met.
        """
        from api.models import GeneratedReport
        # Get chat history up to now
        history = list(session.messages.order_by('timestamp').values_list('role', 'content'))
        
        # Build prompt string
        chat_context = "Chat History:\n"
        for role, content in history[-6:]: # Keep last 6 interactions
            chat_context += f"{role}: {content}\n"
            
        full_prompt = f"{chat_context}\nLatest Request: {latest_user_message}"
        
        # Execute Pipeline (Agent 1 will gatekeep if info is missing)
        try:
            result = ReportGenerationService.execute_two_agent_pipeline(full_prompt)
        except Exception as e:
            return f"I encountered an error trying to process that: {str(e)}"
            
        if result.get("status") == "needs_info":
            return result.get("message")
            
        if result.get("status") == "success":
            file_url = result.get("file_url")
            report_title = result.get("intent_parsed", {}).get("report_title_derived", "Custom Report")
            
            if file_url:
                # Save to DataBase
                GeneratedReport.objects.create(
                    user=session.user,
                    file_url=file_url,
                    title=report_title,
                    # Setting template to None for ad-hoc agentic reports
                )
                return f"Success! I've generated the **{report_title}**. You can download it from the <a href='/portal/reports/'>Reports Library</a>.<br><br>Direct Link: <a href='{file_url}' target='_blank'>Download Here</a>"
            else:
                return f"I generated the {report_title} successfully, but there was an error uploading it to the cloud. Please contact support."
        
        return "Sorry, I am unable to generate the report right now."

class ReportGenerationService:
    @staticmethod
    def _extract_json(text):
        match = re.search(r'```json\n(.*?)```', text, re.DOTALL)
        return match.group(1).strip() if match else text.strip()

    @staticmethod
    def _extract_python_code(text):
        match = re.search(r'```python\n(.*?)```', text, re.DOTALL)
        return match.group(1).strip() if match else text.strip()

    @staticmethod
    def execute_two_agent_pipeline(user_prompt, target_format="xlsx", custom_style=None, output_filename=None):
        """
        Executes the Two-Agent Report Generation Workflow:
        Agent 1: Interprets Intent -> Queries DB securely -> serializes to JSON
        Agent 2: Writes Python script generation code with the JSON context + style format
        """
        # Add cloud storage dependency
        from google.cloud import storage
        from django.conf import settings
        import uuid
        
        _init_vertex()
        
        # ----------------------------------------------------
        # AGENT 1: Intent Parsing & Data Request Generation
        # ----------------------------------------------------
        agent_1 = GenerativeModel("gemini-2.5-pro")
        intent_prompt = f"""
        You are the Data Intent Agent for Finsight.
        Analyze a user's natural language request (and chat history) for a business report.
        
        CRITICAL RULE: You MUST verify if the user has provided the following 4 absolute minimum criteria across their conversation:
        1. Time Period (e.g. "Last 30 Days", "Q3", "All Time")
        2. Report Type (e.g. "Expense Summary", "Budget Overview", "Chart")
        3. Format (Must be one of: "xlsx", "docx", "pptx")
        4. Style (e.g. "Blue Theme", "Corporate Dark", or "Standard")
        
        Available Finsight Schema:
        1. BudgetPool (id, company_id, name, start_date, end_date, total_budget_hkd, remaining_hkd)
        2. Claim (id, user_id, budget_pool_id, status[pending/approved/rejected], amount_hkd, merchant, date, category, note)
        3. ReceiptFile (id, claim_id, ocr_confidence)
        4. GLAccount (id, company_id, name, code, account_type[asset/liability/equity/revenue/expense])
        5. GLTransaction (id, company_id, date, description, claim_id)
        6. GLTransactionLine (id, transaction_id, account_id, debit, credit)
        
        User Request: "{user_prompt}"

        Respond STRICTLY in a JSON format matching this structure:
        {{
            "ready_to_generate": boolean (false if any of the 4 required parameters are missing),
            "missing_info_message": "If ready_to_generate is false, phrase a polite, helpful question asking ONLY for the missing fields.",
            "target_format": "xlsx/docx/pptx or null",
            "style_intent": "A brief description of the style they want, or null",
            "requires_claims_data": boolean,
            "requires_budget_pool_data": boolean,
            "requires_gl_data": boolean,
            "filters": {{
                "date_start": "YYYY-MM-DD or null",
                "date_end": "YYYY-MM-DD or null",
                "status": "approved/pending/rejected/null",
                "category": "category name or null"
            }},
            "report_title_derived": "A succinct title for the report"
        }}
        """
        res_1 = agent_1.generate_content(intent_prompt)
        intent_data = json.loads(ReportGenerationService._extract_json(res_1.text))
        
        # Gatekeeper logic: Stop and ask for info if we don't have all 4
        if not intent_data.get("ready_to_generate"):
            return {
                "status": "needs_info",
                "message": intent_data.get("missing_info_message", "Please clarify your time period, report type, format, and style.")
            }
            
        target_format = intent_data.get("target_format", target_format)
        
        # ----------------------------------------------------
        # DJANGO ORM DATA INGESTION
        # ----------------------------------------------------
        report_context_dict = {}
        
        if intent_data.get("requires_claims_data"):
            # Simple retrieval for MVP - Future iteration can apply 'filters' logic
            claims = Claim.objects.all().values('id', 'merchant', 'amount_hkd', 'date', 'category', 'status')
            report_context_dict['claims'] = list(claims)
            
        if intent_data.get("requires_budget_pool_data"):
            pools = BudgetPool.objects.all().values('id', 'name', 'total_budget_hkd', 'remaining_hkd')
            report_context_dict['budget_pools'] = list(pools)
            
        if intent_data.get("requires_gl_data"):
            gls = GLTransaction.objects.all().values('id', 'date', 'description')
            report_context_dict['gl_transactions'] = list(gls)

        # JSON Serialized safe context
        report_context = json.dumps(report_context_dict, cls=DjangoJSONEncoder)

        # ----------------------------------------------------
        # AGENT 2: Visual Code Generation & Injection
        # ----------------------------------------------------
        agent_2 = GenerativeModel("gemini-2.5-pro")
        
        library_map = {
            "xlsx": ("openpyxl", "from openpyxl import Workbook"),
            "docx": ("python-docx", "from docx import Document"),
            "pptx": ("python-pptx", "from pptx import Presentation")
        }
        
        # Setup defaults
        required_library, required_import = library_map.get(target_format, ("openpyxl", "from openpyxl import Workbook"))
        # In cloud run, the safest place to write execution output is /tmp
        import os
        tmp_dir = "/tmp" if os.environ.get("K_SERVICE") else "."
        file_name_output = os.path.join(tmp_dir, f"agentic_output_flow.{target_format}").replace('\\', '/')
        
        # Merge custom_style and style_intent if provided
        extracted_style_intent = intent_data.get('style_intent', '')
        style_injection = f"Use this visual style theme/rule: {custom_style if custom_style else extracted_style_intent}"

        agent_2_prompt = f"""
        You are the Report Code Generation Agent. Write a standalone Python script to generate a report file.
        
        REQUIREMENTS:
        - Library to use: {required_library}
        - Required imports: MUST include '{required_import}' at the top of the file!
        - Output File Name: MUST use the exact string '{file_name_output}' when saving.
        - User Request: {user_prompt}
        - Derived Title: {intent_data.get('report_title_derived')}
        - Style Requirements: {style_injection}

        DATA PAYLOAD:
        {report_context}

        CRITICAL RULES:
        - Parse the DATA PAYLOAD JSON string directly inside your python code to populate the tables/charts.
        - You MUST end your script by saving the file exactly to '{file_name_output}'. Do NOT give it a different name. Do NOT place it in a subfolder. Example: `prs.save('{file_name_output}')`
        - Do NOT wrap your code in a main function or use `if __name__ == "__main__":`. Write the procedural code directly so it executes immediately.
        - Do NOT import os, sys, or subprocess. Only use safe formatting libraries.
        - Do NOT provide markdown explanation. ONLY output raw Python code wrapped in ```python ... ```
        """

        res_2 = agent_2.generate_content(agent_2_prompt)
        generated_code = ReportGenerationService._extract_python_code(res_2.text)

        # Save for debug traceability
        debug_script_name = "debug_generated_script.py"
        with open(debug_script_name, "w", encoding="utf-8") as f:
            f.write(generated_code)

        # Execute safe sandbox
        exec_namespace = {"__name__": "__main__"}
        try:
            exec(generated_code, exec_namespace)
        except Exception as e:
            raise Exception(f"Failed to execute AI Generated Script: {e}. Check {debug_script_name}")

        import os
        if not os.path.exists(file_name_output):
            print(f"DEBUG SCRIPT CONTENT:\n{generated_code}")
            raise Exception(f"AI Script executed but failed to create the file '{file_name_output}'.")

        # ----------------------------------------------------
        # UPLOAD TO GOOGLE CLOUD STORAGE
        # ----------------------------------------------------
        public_url = ""
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(settings.GS_BUCKET_NAME)
            
            # Keep only the base filename for the GCS blob name
            base_filename = os.path.basename(file_name_output)
            unique_filename = f"reports/{uuid.uuid4().hex}_{base_filename}"
            
            blob = bucket.blob(unique_filename)
            blob.upload_from_filename(file_name_output)
            
            # Delete local file after upload due to Cloud Run statelessness
            import os
            if os.path.exists(file_name_output):
                os.remove(file_name_output)
                
            public_url = f"https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/{unique_filename}"
        except Exception as e:
            print(f"GCS Upload Error: {e}")
            public_url = None
            
        return {
            "status": "success",
            "file_url": public_url,
            "file_path": file_name_output,
            "intent_parsed": intent_data,
            "debug_script": debug_script_name,
            "code_generated": generated_code
        }

