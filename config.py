import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_that_should_be_changed'
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit

    # --- Google Generative AI Configuration ---
    # Store your API key securely.
    # It's recommended to set this as an environment variable (e.g., in a .env file or deployment config)
    # like: GOOGLE_API_KEY="AIzaSyDynwuPk0ryM3yTZQPzy5jpH2H6ILpUDno"
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', 'YOUR_API_KEY_HERE_IF_NOT_IN_ENV')
    if GOOGLE_API_KEY == 'YOUR_API_KEY_HERE_IF_NOT_IN_ENV':
        print("WARNING: GOOGLE_API_KEY not set in environment or config. Using placeholder.")
        # As you provided it, let's use it directly for this example if not in env
        GOOGLE_API_KEY = "AIzaSyDynwuPk0ryM3yTZQPzy5jpH2H6ILpUDno" # For demonstration purposes ONLY

    AI_MODEL_NAME = "gemini-1.5-flash-latest"
    # GOOGLE_CLOUD_PROJECT_ID and GOOGLE_CLOUD_LOCATION are usually not needed
    # when using the `google-generativeai` library directly with an API key,
    # as it bypasses Vertex AI endpoints in this specific setup.