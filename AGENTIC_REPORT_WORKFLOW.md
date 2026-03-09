# Agentic Report Generation Workflow (Approach 2)

This document outlines the architecture for the **Dynamic Agentic Reporting** feature in Finsight, where Vertex AI acts as an autonomous coder to generate highly customized Excel and PowerPoint files on the fly.

---

## 1. The Architecture (Single Cloud Run Instance)

To keep infrastructure costs and complexity minimal for the MVP, we will NOT deploy a separate sandbox service. Execution will happen within the main Django Cloud Run server using a **Two-Agent / Pipeline Approach**.

1. **Step 1: Data Retrieval Agent (or LLM intent parser)**
   * The user asks for a report (e.g., "Give me a Q3 Financial Summary").
   * A lightweight LLM call processes the text, extracting query parameters (e.g., `start_date`, `end_date`, `department`).
   * The Django App (`finsight-backend`) securely runs standard Django ORM queries (`GLTransaction.objects.filter(...)`) based on the extracted parameters to fetch the actual numbers.
   * The backend dumps this data into a standardized JSON payload (the `raw_data`).

2. **Step 2: Code Generation Agent**
   * The backend takes the `raw_data` JSON and injects it securely into the Gemini 2.5 Pro System Prompt.
   * The prompt specifies the requested format (`xlsx`, `docx`, or `pptx`) and the appropriate library (`openpyxl`, `python-docx`, or `python-pptx`).
   * The LLM generates the Python styling and output script exactly matching the `raw_data` dictionary.

3. **Step 3: Sanitization & Execution**
   * **Execution:** Wraps the `exec(ai_code)` in a strict `try/except` block to catch any script errors. 
   * **Output:** Saves the resulting file locally to a `/tmp` folder, uploads it to Google Cloud Storage, and returns the download URL to the user.

*Security Note:* By separating the database query (Step 1) from the code execution (Step 3), the generated python script never needs direct DB access. Furthermore, because `exec()` is running on your main server, the System Prompt MUST strictly forbid the AI from using `os`, `sys`, or `subprocess` modules to prevent hallucinated destructive commands.

---

## 2. Multi-Format Capabilities

The AI dynamically adjusts its generated code based on the required file extension:
*   **`.xlsx` (Financial Statements):** The system prompt injects instructions to use the `openpyxl` library.
*   **`.docx` (Text Reports/Summaries):** The system prompt injects instructions to use the `python-docx` (`import docx`) library.
*   **`.pptx` (Presentations/Decks):** The system prompt injects instructions to use the `python-pptx` (`import pptx`) library.

To allow the AI to match a company's existing report styles without expensive fine-tuning models:

1. Admin clicks **"Upload Style Reference"** and uploads an old PDF or image of a current company report.
2. The image is saved in Cloud Storage.
3. When the user asks to generate a report, Django passes the user's prompt **AND the uploaded image** to Gemini 1.5 Pro.
4. **Prompt payload:** *"Look at the attached image of the company's old report. Extract the exact hex color codes, font weights, and border styles you see. Apply these exact visual styles to the openpyxl Python script you are about to write."*
5. The AI naturally mimics the visual structure it "sees" in the code it generates.

---

## 3. Data Ingestion Contract

To ensure the AI always knows how to loop through your data, you must provide a consistent, flattened data structure. The AI script should always assume a dictionary named `DATA` will be injected into its environment before execution.

```json
[
  {"account_code": "1000", "account_name": "Cash", "amount": 25000, "category": "Asset"},
  {"account_code": "5010", "account_name": "Travel Expense", "amount": 7700, "category": "Expense"}
]
```

## 4. MVP Limitations & Scope

For the MVP, we will run the `exec()` command locally to prove the concept works. For the production MVP on Google Cloud Run, we will implement the Execution Sandbox to ensure the main platform remains stable.