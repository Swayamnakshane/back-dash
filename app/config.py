import os
from dotenv import load_dotenv
from datetime import timezone, timedelta

load_dotenv()

class Config:
    MONGODB_SETTINGS = {
        'host': os.getenv("MONGO_URI", "mongodb://localhost:27017/employee_management")
    }
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_secret_key")

IST = timezone(timedelta(hours=5, minutes=30))
