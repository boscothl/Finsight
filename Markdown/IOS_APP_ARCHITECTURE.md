# iOS App Architecture (Expo React Native)

## Overview
The mobile app is designed as a cross-platform prototype configured specifically for iOS testing via **Expo Go**. It leverages React Native to deliver a native feel while allowing rapid MVP development. 

The primary business goal of this app is to serve as the **Employee Interface** for the Finsight MVP. It enables employees to securely log in, visualize their assigned budget pools, capture receipts (interfacing with Document AI), track previous claim statuses, and consult an AI compliance assistant.

## File Structure & Routing
The app uses **Expo Router** (file-based routing) to manage navigation seamlessly.

```text
mobile_app/
  ├── app/                        # Expo Router configuration
  │   ├── _layout.tsx             # Root stack navigator mapping screens
  │   ├── index.tsx               # Login Screen (Initial route)
  │   ├── scan.tsx                # Scan/Upload receipt screen (Full screen stack)
  │   ├── past-uploads.tsx        # History & Pending claims screen
  │   ├── edit-claim.tsx          # Action Required editing screen
  │   └── (tabs)/                 # Bottom Tab Navigator Layout
  │       ├── _layout.tsx         # Configures the 3 bottom navigation icons
  │       ├── home.tsx            # Home/Overview with Budget visualizer
  │       ├── chatbot.tsx         # Employee AI Chatbot for compliance
  │       └── notifications.tsx   # Mock Notification / Status changes page
  ├── services/                   # Backend Communication
  │   └── api.ts                  # Axios configuration for Django Cloud Run endpoints
  ├── assets/                     # Icons, Splash screens, Fonts
  └── app.json                    # Application identity and Expo permissions
```

### Page Layouts & Flow
1. **Login (`/`):** The entry point. Takes company email and password. On success, pushes to the main tab interface.
2. **Home (`/(tabs)/home`):** The overview dashboard. Displays the core "Budget Pool Usage" progress bar. Features two main action buttons mapping to `scan` and `past-uploads`.
3. **Scan Receipt (`/scan`):** Employs `expo-image-picker` to trigger the physical camera or gallery. It simulates a loading delay, extracting the image URI which will be sent to the backend. Upon OCR extraction, it displays the structured output (Merchant, Amount, Date) for user confirmation before submitting the official claim.
4. **Past Uploads (`/past-uploads`):** Displays a flat list of historical claims. Visually distinguishes states (Approved, Rejected, Pending, Action Required). Clicking "Action Required" items forwards the user parameters to `/edit-claim`.
5. **Chatbot (`/(tabs)/chatbot`):** A conversational UI that interacts with the backend LLM endpoints to answer policy limit queries reliably based on company-specific configurations.

## API & Backend Connection
The React Native app acts as a **stateless client**. It does *not* interface directly with the PostgreSQL database. Instead, it interacts securely with the Django backend (which will be hosted on Google Cloud Run) through standard REST API requests over HTTPS.

### Mechanism (`services/api.ts`)
The connection relies on the `axios` library configured with a base URL pointing directly to the Django server. 

**Connection Flow:**
1. **Action Triggered:** User taps "Upload" or "Login".
2. **Data Formatting:** The mobile app captures the native data. For OCR, it formats the captured native image URI into a standard `FormData` object using `'multipart/form-data'`. For Chatbot messages or Logins, it uses `application/json`.
3. **Request Sent:** Axios dispatches an asynchronous `POST` or `GET` request matching the web portal's existing API views (`api/views.py`).
4. **Backend Processing (Cloud Run):** Django receives the request, validates the user token/session, offloads images to Google Document AI, awaits the resulting parsed map, and saves initial instances to the Database.
5. **JSON Return:** Django returns standard JSON:
   ```json
   {
     "status": "success",
     "extracted_data": {
       "merchant": "XYZ Tech",
       "amount": 1250,
       "date": "2026-03-24"
     }
   }
   ```
6. **UI Update:** The React Native app parses the JSON and sets the local React state (`setOcrResult`), rendering the success fields in the UI.

### Integration Requirements
To successfully link the iOS app to the current Django web app architecture:
- Django views located in `/api` must have JSON-returning views handling Mobile consumption (distinct from standard HTML rendering if currently mixed).
- Web security features like CSRF should be managed for mobile compatibility (usually swapping Session Auth for native Bearer Tokens or JWTs on the mobile side).