# Finsight MVP Refinement Plan

This document outlines the refined feature specifications for the Finsight Admin Portal (Phase 2), focusing on a unified user experience and enhanced functionality for the Dashboard, Approvals, and Reporting modules.

## 1. Global UI/UX Unification
**Objective:** Create a consistent, coherent interface across all admin pages.
*   **Navigation:** Adopting the **Top Navigation Bar** as the standard layout. The Sidebar from the current Dashboard will be removed.
*   **Theme:** Consistent color palette (Indigo/White/Gray) and card styling (rounded corners, soft shadows).
*   **Responsiveness:** All pages will use a centered `max-width` container for main content.

---

## 2. Dashboard Page (`/portal/dashboard/`)
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

## 3. Approvals Page (`/portal/approval/`)
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

## 4. Report & Chatbot Page (`/portal/chatbot/`)
**Goal:** distinct flows for creating new reports vs. reusing successful templates.

### Layout Reorganization (Two-Pane Layout)
**Left Panel: Report Library**
1.  **Saved Templates:**
    *   List of previously generated/saved report configurations (e.g., "Monthly Inv Report - Corporate Style").
    *   *Action:* "Load Template" button to populate the settings.
2.  **Create New:**
    *   Button to clear context and start fresh.

**Right Panel: Generation Workspace**
1.  **Interactive Chat Interface:**
    *   Natural language input ("Create a summary for Q3 travel expenses").
    *   Rich responses (files, preview charts).
2.  **Context Configuration:**
    *   Dropdowns for manual overrides (Date Range, Style) if not using Chat.
3.  **Download Center:**
    *   Persistent list of generated files available for download during the session.

### Data Requirements
*   `ReportTemplate` Model: Stores `name`, `config_json`, `style_preference`.
*   `ChatbotService`: Endpoint to handle "Generate" intent.

---

## Next Implementation Steps
1.  **Refactor Base Template:** Move navigation to `base.html` and standardise CSS.
2.  **Update Dashboard View:** Compute alerts and fetch chart data.
3.  **Enhance Approval View:** Add Modal logic and History queryset.
4.  **Refactor Chatbot Template:** Implement split layout for Templates vs Chat.
