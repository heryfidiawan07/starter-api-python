import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    db_driver: str = os.getenv("DB_DRIVER", "mysql")
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: str = os.getenv("DB_PORT", "3306")
    db_name: str = os.getenv("DB_NAME", "starter_db")
    db_user: str = os.getenv("DB_USER", "root")
    db_pass: str = os.getenv("DB_PASS", "")

    jwt_secret: str = os.getenv("JWT_SECRET", "default-secret-change-this")
    jwt_access_expire: int = int(os.getenv("JWT_ACCESS_EXPIRE", "15"))
    jwt_refresh_expire: int = int(os.getenv("JWT_REFRESH_EXPIRE", "10080"))

    mail_host: str = os.getenv("MAIL_HOST", "smtp.mailtrap.io")
    mail_port: int = int(os.getenv("MAIL_PORT", "587"))
    mail_user: str = os.getenv("MAIL_USER", "")
    mail_pass: str = os.getenv("MAIL_PASS", "")
    mail_from: str = os.getenv("MAIL_FROM", "noreply@example.com")
    mail_from_name: str = os.getenv("MAIL_FROM_NAME", "Starter API")

    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    facebook_client_id: str = os.getenv("FACEBOOK_CLIENT_ID", "")
    facebook_client_secret: str = os.getenv("FACEBOOK_CLIENT_SECRET", "")

    storage_path: str = os.getenv("STORAGE_PATH", "./storage/photos")
    app_url: str = os.getenv("APP_URL", "http://localhost:8000")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    email_verification_required: bool = os.getenv("EMAIL_VERIFICATION_REQUIRED", "false").lower() == "true"


settings = Settings()
