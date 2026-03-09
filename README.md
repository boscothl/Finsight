# Finsight - Setup and Testing Guide

This guide provides step-by-step instructions on how to set up your local development environment, start the Django web server, and test the core functionalities (like the Google Cloud Vertex AI chatbots).

---

## 1. Environment Setup

Before starting the server or testing scripts, ensure your Python virtual environment is activated and dependencies are installed.

**Open your terminal and run:**
```powershell
# 1. Activate the virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# 2. Install all required dependencies
pip install -r requirements.txt
```

---

## 2. Database Setup

This project uses a local SQLite database (`db.sqlite3`) for MVP development. If you pull new model changes, you need to apply them to the database.

**Run the following commands:**
```powershell
# Generate the migration scripts based on models.py
python manage.py makemigrations api
python manage.py makemigrations portal

# Apply the migrations to build the tables in db.sqlite3
python manage.py migrate

# (Optional) Create an admin account so you can log into the Django Admin panel
python manage.py createsuperuser
```

---

## 3. Starting the Django Server

Once the database is set up, you can start the local development web server.

**Run the server:**
```powershell
python manage.py runserver
```

**Where to view it:**
*   **Web Portal:** Open your browser and navigate to `http://localhost:8000/portal/login/`
*   **Django Admin Backend:** Navigate to `http://localhost:8000/admin/`

---

## 4. Testing Vertex AI (Chatbots)

Before integrating AI heavily into the Django views, we test it in an isolated standalone script: `test_vertex.py`.

### Prerequisites for AI Testing
You must authenticate your local terminal with Google Cloud.
```powershell
# 1. Install Google Cloud SDK (CLI) if you haven't already
# 2. Login to your Google account with application default credentials:
gcloud auth application-default login
```
*(Note: `test_vertex.py` currently hardcodes the credential path so it works out-of-the-box, but standard `gcloud` login is best practice).*

### Running the Test Script
We have two AI personas to test: The **Compliance Bot** (RAG) and the **Report Generation Bot** (Structured JSON output).

1. Open `test_vertex.py` in your editor.
2. Scroll to the bottom of the file to the `if __name__ == "__main__":` block.
3. **To test the Compliance Bot:**
   ```python
   test_compliance_bot()
   # test_report_bot()
   ```
4. **To test the Report Bot:**
   ```python
   # test_compliance_bot()
   test_report_bot()
   ```
5. Run the file in your terminal:
   ```powershell
   python test_vertex.py
   ```

### Troubleshooting
*   **Missing Module (`ModuleNotFoundError: No module named 'vertexai'`)**: This means your virtual environment is either not activated, or the package wasn't installed. Make sure `.venv` shows in your terminal prompt, then run `pip install google-cloud-aiplatform`.
*   **Google Auth Errors**: Ensure you have run `gcloud auth application-default login` OR that the `GOOGLE_APPLICATION_CREDENTIALS` path inside `test_vertex.py` points to a valid JSON service account key.

---

## 5. Deployment (Google Cloud Run)

This project is packaged with a `Dockerfile` and is designed to be deployed to **Google Cloud Run** for a serverless, scalable backend.

### 5.1 Pre-deployment Checklist
Before deploying to production, make sure to update your `requirements.txt`:
1. Uncomment `gunicorn` (required for serving the app in the Docker container).
2. Uncomment `psycopg2-binary` if you are switching from the local SQLite database to a **Google Cloud SQL (PostgreSQL)** instance.

### 5.2 Build and Deploy via Google Cloud CLI
You can build and deploy the container directly using the `gcloud` CLI. Ensure you are in the root directory (where the `Dockerfile` is located).

```powershell
# 1. Set your project ID
gcloud config set project YOUR_PROJECT_ID

# 2. Build the Docker image and submit it to Google Cloud Build, then deploy to Cloud Run
gcloud run deploy finsight-backend `
  --source . `
  --region asia-east1 `
  --allow-unauthenticated `
  --port 8080 `
  --set-env-vars="DEBUG=False,SECRET_KEY=your_production_secret"
```

### 5.3 Connecting to Cloud SQL (Production Database)
In production, Cloud Run should not use the local `db.sqlite3` because Cloud Run containers are stateless (data will be lost when the container shuts down). 

1. Create a **Cloud SQL for PostgreSQL** instance in Google Cloud Console.
2. When deploying to Cloud Run, add the Cloud SQL connection and your database URL. Add this to your `gcloud run deploy` command:
   ```powershell
   --add-cloudsql-instances="YOUR_PROJECT_ID:asia-east1:YOUR_INSTANCE_NAME" `
   --set-env-vars="DATABASE_URL=postgres://db_user:db_password@/db_name?host=/cloudsql/YOUR_PROJECT_ID:asia-east1:YOUR_INSTANCE_NAME"
   ```

### 5.4 Running Production Migrations
Since Cloud Run is serverless, you cannot easily run `python manage.py migrate` directly on the server. The best ways to apply database migrations in production are:
*   **Locally via Cloud SQL Auth Proxy**: Connect your local machine to the production database and run `python manage.py migrate`.
*   **Cloud Run Jobs**: Create a Cloud Run Job that executes `python manage.py migrate` and run it during your CI/CD pipeline before deploying the main service.
