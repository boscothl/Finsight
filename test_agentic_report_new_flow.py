import os
import re
import json
import django
import vertexai
from vertexai.generative_models import GenerativeModel

# --- DJANGO SETUP ---
# Standard procedure to run standalone scripts that need Django models.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Finsight.settings')
django.setup()

from api.models import Claim, GLTransaction
from django.core.serializers.json import DjangoJSONEncoder

# --- GCP SETUP ---
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expandvars(r"%APPDATA%\gcloud\application_default_credentials.json")
PROJECT_ID = "finsight-484914"
LOCATION = "us-central1" 
vertexai.init(project=PROJECT_ID, location=LOCATION)

def extract_python_code(text):
    match = re.search(r'```python\n(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def extract_json(text):
    match = re.search(r'```json\n(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def run_two_agent_pipeline(user_prompt, target_format="xlsx", custom_style=None):
    print(f"\n--- TESTING TWO-AGENT WORKFLOW ({target_format.upper()}) ---")
    print(f"User Request: '{user_prompt}'\n")

    # ==========================================
    # AGENT 1: Intent Parsing & Data Parameterization
    # ==========================================
    print("[Agent 1: Processing Intent & Data Structure]")
    agent_1 = GenerativeModel("gemini-2.5-pro")
    intent_prompt = f"""
    You are the Data Intent Agent for an internal finance system called Finsight.
    Your job is to analyze a user's natural language request for a business report, and determine EXACTLY which database tables and filters are needed to fulfill it.
    
    Here is the full Finsight Database Schema available to you:
    
    1. BudgetPool (id, company_id, name, start_date, end_date, total_budget_hkd, remaining_hkd)
    2. Claim (id, user_id, budget_pool_id, status[pending/approved/rejected], amount_hkd, merchant, date, category, note)
    3. ReceiptFile (id, claim_id, ocr_confidence)
    4. GLAccount (id, company_id, name, code, account_type[asset/liability/equity/revenue/expense])
    5. GLTransaction (id, company_id, date, description, claim_id)
    6. GLTransactionLine (id, transaction_id, account_id, debit, credit)
    
    User Request: "{user_prompt}"

    Analyze the request and return ONLY a JSON specifying the data parameters we need to fetch. 
    Format your response EXACTLY like this JSON block:
    {{
        "requires_claims_data": true or false,
        "requires_budget_pool_data": true or false,
        "requires_gl_data": true or false,
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
    intent_data = json.loads(extract_json(res_1.text))
    print(f"  -> Extracted Intent: {intent_data['report_title_derived']}")

    # --- PYTHON "polling": Fulfilling the Data Contract safely outside the LLM ---
    print("\n[System: Polling Django Database securely...]")
    report_context = []
    if intent_data.get("requires_claims_data"):
        # Fetching actual DB data. In a real scenario, we apply filters based on intent_data.
        claims = Claim.objects.all().values('id', 'merchant', 'amount_hkd', 'date', 'category', 'status')
        # Serialize to JSON string nicely
        report_context = json.dumps(list(claims), cls=DjangoJSONEncoder)
        print(f"  -> Retrieved {claims.count()} records from Django DB securely.")
    else:
        report_context = "[]"
        print("  -> No data required from DB based on intent.")

    # ==========================================
    # AGENT 2: Code Generation
    # ==========================================
    print(f"\n[Agent 2: Generating Python Code for {target_format.upper()} Report]")
    agent_2 = GenerativeModel("gemini-2.5-pro")
    
    library_map = {
        "xlsx": "openpyxl",
        "docx": "python-docx (import docx)",
        "pptx": "python-pptx (import pptx)"
    }
    required_library = library_map.get(target_format, "openpyxl")
    file_name = f"agentic_output_flow.{target_format}"

    style_injection = f"Use this visual style theme: {json.dumps(custom_style)}" if custom_style else "Use a clean, corporate standard style."
    
    agent_2_prompt = f"""
    You are the Report Code Generation Agent. Write a standalone Python script to generate the file.
    
    REQUIREMENTS:
    - Library to use: {required_library}
    - Output File Name: {file_name}
    - User Request: {user_prompt}
    - Derived Title: {intent_data.get('report_title_derived')}
    - Style Requirements: {style_injection}
    
    DATA PAYLOAD (from secure DB pipeline):
    {report_context}
    
    CRITICAL SECURITY RULES:
    - Parse the DATA PAYLOAD JSON string inside your python code to populate the document.
    - Do NOT import os, sys, or subprocess.
    - Do NOT provide any markdown text explanation. ONLY output the raw Python code wrapped in ```python ... ```
    """

    res_2 = agent_2.generate_content(agent_2_prompt)
    generated_code = extract_python_code(res_2.text)
    
    print("  -> Generative code received.\n")
    print("--- GENERATED CODE SNIPPET (First 15 lines) ---")
    print('\n'.join(generated_code.split('\n')[:15]))
    print("----------------------------------------------")

    # ==========================================
    # EXECUTION STAGE
    # ==========================================
    print(f"\n[System: Executing Code via exec()...]")
    
    # Save the generated code to a file so we can debug it if it fails!
    debug_file_name = "debug_generated_script.py"
    with open(debug_file_name, "w", encoding="utf-8") as f:
        f.write(generated_code)
    print(f"  -> Saved generated python code to '{debug_file_name}' for inspection.")

    try:
        # NOTE: exec() is used locally. In cloud, we submit 'generated_code' to Cloud Run.
        # We need to pass an empty dictionary for locals/globals so imports don't leak out 
        # or fail due to scoping, but for this simple script a basic exec is okay.
        # It's safer to run it in its own namespace:
        exec_namespace = {}
        exec(generated_code, exec_namespace)
        if os.path.exists(file_name):
            print(f"✅ SUCCESS! '{file_name}' was successfully generated based on Live Database Data!")
    except Exception as e:
        print(f"❌ Execution Failed: {e}")
        print(f"👉 Please open '{debug_file_name}' to see exactly what caused the error.")

if __name__ == "__main__":
    # Test 1: Simple Excel Expense Report
    sample_style = {
        "colors": {"primary": "#002060", "text": "#ffffff"},
        "fonts": {"primary": "Arial"}
    }
    
    # We run the flow!
    run_two_agent_pipeline(
        user_prompt="I need an excel sheet breaking down all the system expense claims so far.",
        target_format="xlsx",
        custom_style=sample_style
    )
