from django.core.management.base import BaseCommand
from django.conf import settings
import os

try:
    from google.cloud import storage
    from google.cloud import documentai
    import vertexai
    from vertexai.generative_models import GenerativeModel
    GOOGLE_LIBS_INSTALLED = True
except ImportError:
    GOOGLE_LIBS_INSTALLED = False

class Command(BaseCommand):
    help = 'Checks connection to Google Cloud Services (Storage, Document AI, Vertex AI)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Testing Google Cloud Connections...'))

        # 0. Check Libraries
        if not GOOGLE_LIBS_INSTALLED:
            self.stdout.write(self.style.ERROR('❌ Google Cloud libraries not installed. Run: pip install google-cloud-storage google-cloud-documentai google-cloud-aiplatform'))
            return

        # 1. Check Credentials
        # Note: We support Application Default Credentials (ADC) which do NOT require
        # GOOGLE_APPLICATION_CREDENTIALS to be set if 'gcloud auth application-default login' was used.
        creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if creds_path:
            if not os.path.exists(creds_path):
                self.stdout.write(self.style.ERROR(f'❌ GOOGLE_APPLICATION_CREDENTIALS path not found: {creds_path}'))
                return
            self.stdout.write(self.style.SUCCESS(f'✅ Using key file via GOOGLE_APPLICATION_CREDENTIALS: {creds_path}'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  GOOGLE_APPLICATION_CREDENTIALS not set. Assuming Application Default Credentials (ADC) are set via `gcloud auth application-default login`.'))

        # 2. Test Cloud Storage
        try:
            storage_client = storage.Client()
            buckets = list(storage_client.list_buckets(max_results=1))
            bucket_name = getattr(settings, 'GS_BUCKET_NAME', 'unknown-bucket')
            self.stdout.write(self.style.SUCCESS(f'✅ Cloud Storage: Connected (Project: {storage_client.project})'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Cloud Storage Failed: {str(e)}'))

        # 3. Test Document AI
        try:
            # Just initializing the client is a good first check for auth
            docai_client = documentai.DocumentProcessorServiceClient()
            self.stdout.write(self.style.SUCCESS('✅ Document AI: Client initialized successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Document AI Failed: {str(e)}'))

        # 4. Test Vertex AI
        try:
            project_id = os.environ.get('GCP_PROJECT_ID')
            location = os.environ.get('GCP_LOCATION', 'us-central1')
            if not project_id:
                 self.stdout.write(self.style.WARNING('⚠️ GCP_PROJECT_ID not set, skipping Vertex AI deep check.'))
            else:
                vertexai.init(project=project_id, location=location)
                # Try loading a model representation (doesn't incur cost until prediction)
                # Updated to use gemini-1.5-flash which is the current standard
                model = GenerativeModel("gemini-1.5-flash")
                self.stdout.write(self.style.SUCCESS(f'✅ Vertex AI: Connected to region {location} (Model: gemini-1.5-flash)'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Vertex AI Failed: {str(e)}'))
