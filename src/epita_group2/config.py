import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    api_key: str = os.getenv("IPINFO_TOKEN", "")
    debug: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    def validate(self):
        if not self.api_key or self.api_key.startswith("your_"):
            raise ValueError(
                "CRITICAL SECURITY / CONFIG ERROR: API key is not configured!\n"
                "Ensure your .env file exists and contains IPINFO_TOKEN."
            )

config = Settings()
