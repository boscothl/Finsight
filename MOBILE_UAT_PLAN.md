# Finsight Mobile App - User Acceptance Testing (UAT) Plan

Welcome to the UAT phase! Please go through each checklist item below to verify that the app's functionality works end-to-end on your device. You can check off the boxes as you complete them.

## 1. Authentication & System Startup
- [X] Mobile app launches successfully.
- [X] Login screen accepts valid credentials and authenticates.
- [X] Upon successful login, the user is navigated to the Home Dashboard.
- [X] Background: Django server successfully queries the Google Cloud SQL Database.

## 2. Home Dashboard
- [X] **Greeting**: Displays a "Welcome back" greeting.
- [X] **Budget Pools**: Carousel displays the user's active budget pools, showing total budget, spent amount, and a visual progress bar.
- [X] **UI Fix**: The budget pool carousel's formatting is correctly proportioned (not over-stretched vertically).
- [X] **Recent Claims**: Needs a dedicated view showing all approved/pending/rejected claims. Clicking a claim should display the receipt picture, info, and status.
- [X] **Navigation**: Tapping "Scan Receipt" takes you to the scan screen.
- [X] **Navigation**: Tapping "Ask Policy" takes you to the compliance chatbot screen.

## 3. Receipt Scanning & Upload (`scan.tsx`)
- [X] **UI Fix**: The Close button (X) at the top left successfully exits the modal and returns to the Home Dashboard.
- [X] **Permissions**: Prompts for required Camera/Gallery permissions.
- [X] **Capture**: "Open Camera" successfully opens the camera, allows a photo, and starts the upload.
- [X] **Gallery**: "Upload from Gallery" lets you pick an image and starts the upload.
- [X] **Loading State**: An activity indicator ("Extracting receipt data with AI...") shows while the image is processing on the backend.
- [X] **OCR Review**: Displays the extracted OCR results correctly and allows the user to effectively edit the fields (Merchant, Amount, Date, Category, Note).
- [X] **Claim Submission**: Tapping "Confirm & Submit Claim" sends the final data payload to the server.
- [X] **Claim Success**: A success alert pops up and returns the user to the Home Dashboard.
- [ ] **Data Verification**: Check the Django admin panel (or reload the app) to see if the new claim was successfully created with a "pending" status.

## 4. Compliance Chatbot
- [X] The chat interface renders properly.
- [X] Inputting a question and pressing send adds the message to the chat view.
- [X] A loading indicator appears while waiting for the AI response.
- [X] The app successfully queries the backend (`/chat/compliance/`).
- [X] The bot's response is displayed in the chat history.

## 5. Edge Cases & Error Handling (Optional/Bonus)
- [ ] What happens if a receipt image is blurry or unreadable? (Should show an error or fallback gracefully).
- [ ] What happens if the claim submission fails? (Should show a "Failed to submit claim" alert).
- [ ] What happens if network connection is lost?
## 6. Upcoming Features (To-Do)
- [ ] **Working Notification Workflow**: Ensure users receive notifications on claim updates and key action events (To be implemented).

## 7. Website Integration & Ongoing Fixes
- [X] **Real Data on Desktop Approval Page**: The web portal's approval page correctly receives the new claim from mobile, but needs to be updated to show the actual extracted/user-edited data instead of dummy variables.
- [X] **Display Invoice Image**: The web approval portal must display the uploaded receipt/invoice image alongside the claim details for manager verification.
