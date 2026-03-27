# Mobile UI + Django Connection Architecture (Expo React Native)

## Purpose
This document explains:
1. How the mobile UI is structured.
2. How each mobile screen connects to Django APIs.
3. How JWT authentication is handled between mobile and server.

The mobile app is an Expo React Native client for the Finsight employee workflow: login, budget overview, receipt upload OCR, claim history, and compliance chat.

## 1) Mobile UI Structure

### Routing and Navigation
The app uses Expo Router with a root stack plus a tab group.

```text
mobile_app/
  app/
    _layout.tsx                 # Root stack navigator
    index.tsx                   # Login screen
    scan.tsx                    # Camera/gallery receipt upload screen
    past-uploads.tsx            # Claims history list
    edit-claim.tsx              # Edit flow for returned/pending claim
    (tabs)/
      _layout.tsx               # Bottom tabs: Home / Chatbot / Notifications
      home.tsx                  # Budget pools + quick actions
      chatbot.tsx               # Chat UI (currently local bot response)
      notifications.tsx         # Notification screen (UI-only)
  services/
    api.ts                      # Axios client + auth interceptors + API methods
```

### Screen Responsibilities
1. Login (`app/index.tsx`)
- Collects username/password.
- Calls Django JWT login endpoint.
- Stores access/refresh tokens in AsyncStorage.
- Navigates to tabs on success.

2. Home (`app/(tabs)/home.tsx`)
- Calls `GET /api/mobile/home/`.
- Renders budget pools in a horizontal swipe carousel.
- Displays a quick recent-claims count.
- Provides quick navigation buttons to Scan and Past Uploads.

3. Scan (`app/scan.tsx`)
- Uses `expo-image-picker` camera/gallery.
- Uploads image as multipart form data to Django.
- Receives OCR extraction response and renders merchant/amount/date.

4. Past Uploads (`app/past-uploads.tsx`)
- Calls `GET /api/mobile/claims/`.
- Displays claim status cards (Approved, Pending, Rejected, Returned).
- Routes eligible items to Edit Claim flow.

5. Chatbot (`app/(tabs)/chatbot.tsx`)
- UI exists and API helper is ready in `services/api.ts`.
- Current screen logic still uses local mocked response text.
- Next small step: replace local reply with `sendComplianceQuestion()` call.

## 2) How Mobile Connects to Django

### Base API Client
`mobile_app/services/api.ts` is the single API gateway for the app.

Key responsibilities:
1. Axios instance with base URL:
- `EXPO_PUBLIC_API_BASE_URL` (preferred for device testing), fallback to `http://localhost:8000/api`.

2. JWT token persistence:
- Access token key: `finsight_access_token`
- Refresh token key: `finsight_refresh_token`
- Stored in AsyncStorage.

3. Authorization header injection:
- Request interceptor reads access token.
- Adds `Authorization: Bearer <token>` to outgoing requests.

4. Automatic refresh on 401:
- Response interceptor calls `/auth/refresh/` once per concurrent refresh cycle.
- Replays original request after access token renewal.

### Request Lifecycle
1. User action in a screen triggers a service method in `api.ts`.
2. Axios interceptor attaches Bearer token (if available).
3. Django endpoint processes request with DRF + JWT auth.
4. JSON response returns to screen state and UI updates.

## 3) Django Side Structure

### URL Layer
`api/urls.py` exposes mobile endpoints:

```text
POST /api/auth/login/
POST /api/auth/refresh/
GET  /api/mobile/home/
GET  /api/mobile/budget-pools/
GET  /api/mobile/claims/
POST /api/mobile/upload-receipt/
POST /api/chat/compliance/
```

### View Layer
`api/views.py` contains API views for mobile:
1. `MobileHomeView` -> pools + recent claims for logged-in user.
2. `MobileBudgetPoolsView` -> budget pool list.
3. `MobileClaimsView` -> claims list.
4. `MobileUploadReceiptView` -> receives image file and calls DocumentAI service.
5. `compliance_chat_view` -> currently a stubbed policy answer endpoint.

### Service Layer
`api/services.py` currently includes:
1. `DocumentAIService.extract_receipt(...)`
- Optionally uploads receipt to GCS (if bucket configured).
- Sends content to Google Document AI (if processor configured).
- Returns parsed fields (merchant, amount, date, currency).

### Authentication Config
`Finsight/settings.py` uses DRF JWT authentication:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}
```

## 4) Current Endpoint Mapping (Mobile -> Django)

1. `login(username, password)`
- Mobile: `services/api.ts`
- Django: `POST /api/auth/login/`

2. `fetchHomeData()`
- Mobile: `app/(tabs)/home.tsx`
- Django: `GET /api/mobile/home/`

3. `fetchClaims()`
- Mobile: `app/past-uploads.tsx`
- Django: `GET /api/mobile/claims/`

4. `uploadReceipt(imageUri)`
- Mobile: `app/scan.tsx`
- Django: `POST /api/mobile/upload-receipt/`

5. `sendComplianceQuestion(query)`
- Mobile helper exists in `services/api.ts`
- Django: `POST /api/chat/compliance/`
- UI wiring still pending in chatbot screen.

## 5) Environment Notes for iOS Testing

For real iPhone testing, do not use localhost unless tunneling.

Set:
`EXPO_PUBLIC_API_BASE_URL=http://<YOUR_COMPUTER_LAN_IP>:8000/api`

Examples:
1. Same Wi-Fi local Django server.
2. Public HTTPS Cloud Run endpoint.

Also ensure Django allows the mobile origin/network path and is reachable from the device.

## 6) Quick Summary
The architecture is now layered and clean:
1. UI screens in Expo Router.
2. Single API service module with JWT + auto-refresh.
3. DRF JWT-protected Django endpoints.
4. Receipt OCR flow through Django service layer to GCS/Document AI.

This makes the mobile client simple, while keeping business logic and cloud integration inside Django.