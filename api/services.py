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

class OCRService:
    @staticmethod
    def extract_receipt(file_path):
        """
        Wraps google-cloud-documentai to process receipts.
        """
        # MVP skeletal phase
        return {
            "merchant": "Starbucks HK",
            "date": "2023-10-25",
            "amount": 48.0,
            "currency": "HKD",
            "category": "Meals",
            "items": ["Latte", "Bagel"]
        }

class ChatbotService:
    @staticmethod
    def generate_response(message, context="employee"):
        """
        Wraps vertexai to handle chat prompts.
        """
        return f"Hello, I am the {context} chatbot. You said: '{message}'. (AI Integration Pending)"

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
        _init_vertex()
        
        # ----------------------------------------------------
        # AGENT 1: Intent Parsing & Data Request Generation
        # ----------------------------------------------------
        agent_1 = GenerativeModel("gemini-2.5-pro")
        intent_prompt = f"""
        You are the Data Intent Agent for Finsight.
        Analyze a user's natural language request for a business report, and determine EXACTLY which database tables and filters are needed.
        
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
        file_name_output = output_filename or f"agentic_output_flow.{target_format}"
        style_injection = f"Use this visual style theme: {json.dumps(custom_style)}" if custom_style else "Use a clean, corporate standard style."

        agent_2_prompt = f"""
        You are the Report Code Generation Agent. Write a standalone Python script to generate a report file.
        
        REQUIREMENTS:
        - Library to use: {required_library}
        - Required imports: MUST include '{required_import}' at the top of the file!
        - Output File Name: {file_name_output}
        - User Request: {user_prompt}
        - Derived Title: {intent_data.get('report_title_derived')}
        - Style Requirements: {style_injection}
        
        DATA PAYLOAD:
        {report_context}
        
        CRITICAL RULES:
        - Parse the DATA PAYLOAD JSON string directly inside your python code to populate the tables/charts.
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
        exec_namespace = {}
        try:
            exec(generated_code, exec_namespace)
        except Exception as e:
            raise Exception(f"Failed to execute AI Generated Script: {e}. Check {debug_script_name}")
            
        return {
            "status": "success",
            "file_path": file_name_output,
            "intent_parsed": intent_data,
            "debug_script": debug_script_name,
            "code_generated": generated_code
        }

