import os
from django.core.management.base import BaseCommand
from google.cloud import storage
from google.cloud import documentai
from google.cloud import aiplatform

class Command(BaseCommand):
    help = 'Test Google Cloud Platform connections for Document AI, Vertex AI, and Storage'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Google Cloud Platform connections...'))
        
        # Check if GOOGLE_APPLICATION_CREDENTIALS is set
        creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path:
            self.stdout.write(self.style.ERROR('ERROR: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.'))
            return

        if not os.path.exists(creds_path):
             self.stdout.write(self.style.ERROR(f'ERROR: Credentials file not found at {creds_path}'))
             return

        self.stdout.write(f'Using credentials from: {creds_path}')

        # 1. Test Google Cloud Storage
        try:
            storage_client = storage.Client()
            buckets = list(storage_client.list_buckets(max_results=1))
            self.stdout.write(self.style.SUCCESS(f'[SUCCESS] Google Cloud Storage: Connected. Found {len(buckets)} bucket(s) (showing max 1).'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[FAILED] Google Cloud Storage: {str(e)}'))

        # 2. Test Document AI
        try:
            # Just initializing the client is a basic check. 
            # Ideally we would list processors, but that requires a location.
            # We'll try to list processors in 'us' location as a default test.
            project_id = os.environ.get('GCP_PROJECT_ID')
            location = os.environ.get('GCP_LOCATION', 'us') # Default to 'us' if not set

            if project_id:
                opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}
                docai_client = documentai.DocumentProcessorServiceClient(client_options=opts)
                parent = docai_client.common_location_path(project_id, location)
                self.stdout.write(self.style.SUCCESS(f'[SUCCESS] Document AI: Client initialized for project {project_id} in {location}.'))
            else:
                 self.stdout.write(self.style.WARNING('[WARNING] Document AI: GCP_PROJECT_ID not set, skipping detailed check.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[FAILED] Document AI: {str(e)}'))

        # 3. Test Vertex AI
        try:
            project_id = os.environ.get('GCP_PROJECT_ID')
            location = os.environ.get('GCP_LOCATION', 'us-central1')
            
            if project_id:
                aiplatform.init(project=project_id, location=location)
                self.stdout.write(self.style.SUCCESS(f'[SUCCESS] Vertex AI: Initialized for project {project_id} in {location}.'))
            else:
                 self.stdout.write(self.style.WARNING('[WARNING] Vertex AI: GCP_PROJECT_ID not set, skipping initialization.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[FAILED] Vertex AI: {str(e)}'))
