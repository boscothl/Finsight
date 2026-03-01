
PROJECT SUMMARY (MVP / Prototype)

This project delivers a cross‑platform React Native iOS app for employees and a React web admin portal, backed by a Google Cloud backend. The core mission of the MVP is to demonstrate:
- Receipt-to-claim workflow with OCR extraction
- Admin approval and budget pools
- Editable PPTX and Word report generator
- Two chatbots (Employee + Admin) with scoped capabilities
- Minimal infrastructure and roles

1. USER REQUIREMENTS

1.1 Employee Requirements – iOS App
- Email/password login
- Capture one receipt photo
- OCR via Google Document AI (EN + zh-HK)
- Edit extracted fields: date, merchant, amount, category, budget pool
- View pending and history
- Submit claim or save draft
- Employee chatbot for claimability, policy Q&A, status

1.2 Admin Requirements – Web App
- Login
- View and approve/return claims
- Create budget pools (soft warning, approval-based deduction)
- Generate PPTX presentations and Word reports (editable)
- Admin chatbot to create unique report templates and generate content
- CSV export
- Dashboard: spend by pool, pending claims, category spend

1.3 Excluded for MVP
- Multi-level approval, FX, payments, SSO/SCIM, PDFs, card feeds, fraud checks

2. FUNCTIONAL SPECIFICATIONS

2.1 iOS App (React Native)
- Single photo capture
- Send to Document AI
- OCR threshold = 0.8
- Edit fields screen
- Draft and submit state
- Chatbot grounded with internal policy + claim data

2.2 Admin Web App
- Approval queue
- Approve or return with comment
- Budget pool CRUD
- Editable PPTX/DOCX generation
- Dashboard with basic metrics
- CSV export

2.3 Backend Services (Google Cloud)
- Cloud Run API
- Cloud SQL (PostgreSQL)
- Cloud Storage (images)
- Google Document AI
- Vertex AI for chatbots
- PPTX/DOCX generation service

3. DATA MODEL

User: id, email, password_hash, role, name, created_at
BudgetPool: id, name, start_date, end_date, total_budget_hkd, remaining_hkd, created_at
Claim: id, user_id, budget_pool_id, status, amount_hkd, merchant, date, category, note, created_at, updated_at
ReceiptFile: id, claim_id, url, ocr_json, ocr_confidence
Approval: id, claim_id, approver_id, decision, comment, decided_at
PolicyDoc: id, title, version, url, created_at
ReportTemplate: id, name, type, config_json, created_by, created_at

4. SYSTEM ARCHITECTURE
- React Native iOS app
- Django Web 
- Cloud Run backend
- Cloud SQL database
- Cloud Storage
- Document AI
- Vertex AI

5. MVP SCOPE
Included: OCR, claims, approvals, pools, chatbots, ppt/docx, dashboards
Excluded: Multi-level approval, FX, payments, PDFs, SSO, fraud checks

