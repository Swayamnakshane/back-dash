import os
from dotenv import load_dotenv
from datetime import timezone, timedelta

# Load environment variables from .env file
load_dotenv()

class Config:
    # MongoDB Configuration
    MONGODB_SETTINGS = {
        'host': os.getenv("MONGO_URI", "mongodb://localhost:27017/employee_management")
    }

    # Flask Security Keys
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_jwt_secret_key")

    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
    AWS_S3_REGION = os.getenv("AWS_S3_REGION")

    # Additional Flask Config
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    PORT = int(os.getenv("PORT", 5000))

# Optional: IST timezone object
IST = timezone(timedelta(hours=5, minutes=30))
