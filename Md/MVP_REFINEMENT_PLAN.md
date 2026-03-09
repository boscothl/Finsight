# Finsight MVP Refinement Plan

This document outlines the refined feature specifications for the Finsight Admin Portal (Phase 2), focusing on a unified user experience and enhanced functionality for the Dashboard, Approvals, and Reporting modules.

## 1. Global UI/UX Unification
**Objective:** Create a consistent, coherent interface across all admin pages.
*   **Navigation:** Adopting the **Top Navigation Bar** as the standard layout. The Sidebar from the current Dashboard will be removed.
*   **Theme:** Consistent color palette (Indigo/White/Gray) and card styling (rounded corners, soft shadows).
*   **Responsiveness:** All pages will use a centered `max-width` container for main content.

---

## 2. Dashboard Page (`/dashboard/`)
**Goal:** Provide an immediate high-level overview of financial health and actionable alerts.

### KEY Features
1.  **Actionable Alerts Section**
    *   **Budget Warnings:** Highlight Budget Pools > 80% utilization.
    *   **Claim Backlog:** "X Pending Claims requiring attention."
    *   *Implementation:* Computed list passed in context.
2.  **Key Metric Cards**
    *   Total Budget (Aggregated across active pools).
    *   Total Spend (YTD).
    *   Remaining Budget.
    *   Pending Request Count.
3.  **Financial Overview Chart**
    *   *Visual:* Bar chart showing monthly spending vs budget.
    *   *Tech:* Chart.js fed by Django JSON data.
4.  **Recent Activity Feed**
    *   List of 5 most recent system events (New Claim, Approval, Report Generated).

### Data Requirements
*   `BudgetPool`: `total_budget`, `remaining`, `alert_threshold`.
*   `Claim`: `status='pending'`, `created_at`.
*   `Alerts`: Computed list of warning strings.

---

## 3. Approvals Page (`/approval/`)
**Goal:** Efficient processing of claims with deep inspection capabilities and audit trails.

### KEY Features
1.  **Pending Claims Grid**
    *   Cards showing User, Category, Amount, Date.
2.  **Claim Detail Modal**
    *   **Trigger:** Clicking a pending claim card.
    *   **Content:**
        *   **Left Side:** Renders the uploaded receipt image.
        *   **Right Side:** Edtiable OCR extracted fields (Merchant, Date, Total, Tax) for validation.
    *   **Actions:** "Approve" or "Reject" (with mandatory reason input).
3.  **Historical Approval/Reject Log**
    *   A separate section or tab "History".
    *   Table view of processed claims with: Date, User, Status, and **who processed it**.

### Data Requirements
*   `Claim`: `status`, `reviewer_note`, `reviewed_by`, `reviewed_at`.
*   `ReceiptFile`: Image URL.
*   `OCRService`: Extracted JSON data.

---

## 4. Report Builder & Chatbot Page (`/chatbot/`)
**Goal:** Provide two distinct modes for generating custom reports, ranging from quick standard forms to advanced AI-driven creation, supported by a secure "Two-Agent Pipeline."

### KEY Features
1.  **Mode Switcher Component**
    *   **Simple Mode:** A standard, intuitive web form capturing Time Period, Report Type, Format (.xlsx, .docx, .pptx), and Reference Style.
    *   **Advance Mode:** A full-featured chat interface for iterative, natural language report requests and flexible data exploration.
2.  **Style Manager Modal**
    *   Allows users to upload a PDF or image of an existing document.
    *   AI extracts the styling (Colors, Fonts, Layouts) and saves it as a reusable "Theme" (e.g., Corporate Standard Theme, Creative Marketing Theme).
3.  **Chat Iteration & Style Saving**
    *   In Advance Mode, when the bot responds with a generated report or a style mapping block, users can click "Save Extracted Style" to store the settings into the database directly from the chat.
4.  **Secure "Two-Agent" Data Pipeline**
    *   **Step 1 (Data Agent):** Parses the user's intent to identify required constraints, securely polling the Django database to return sanitized JSON payloads.
    *   **Step 2 (Code Gen Agent):** Receives the user prompt and the JSON data array to safely assemble Python scripts (`openpyxl`, `python-docx`, `python-pptx`). This avoids arbitrary `exec()` vulnerabilities involving the database.

---

## 5. Reports Library Page (`/reports/`)
**Goal:** A centralized hub for managing, viewing, and organizing all historically generated or uploaded reports.

### KEY Features
1.  **Report Grid Layout**
    *   Clean CSS-grid displaying recent documents (Excel, Word, PowerPoint) using file-type icons.
2.  **File Management System**
    *   Quick "Download" options for previously generated outputs.
    *   Display of key metadata (Date, format, type, and source).

---

## Next Implementation Steps
1.  **Refactor Base Template:** Move navigation to `base.html` and standardise CSS. *(Completed)*
2.  **Update Dashboard View:** Compute alerts and fetch chart data.
3.  **Enhance Approval View:** Add Modal logic and History queryset.
4.  **Refactor Chatbot Template (`/chatbot/`):** Implement Mode Switcher (Simple vs Advance) and Style Manager modal. *(Completed)*
5.  **Build Reports Page (`/reports/`):** Construct the viewing hub. *(Completed)*
6.  **Wire up the Two-Agent Pipeline:** Implement the backend logic mapping to the new pipeline architecture.
