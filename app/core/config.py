# app/core/config.py

from datetime import timedelta
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, MySQLDsn, PostgresDsn, SecretStr
from pathlib import Path
import urllib.parse
from typing import Literal
from enum import Enum
import os

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load the ENV variable (controls which .env file to load)
ENV = os.getenv("ENV", "local")  # This comes from docker-compose or shell

# Map ENV to actual .env file path
ENV_PATHS = {
    "local": BASE_DIR / "configs/environments/local.env",
    "docker": BASE_DIR / "configs/environments/docker.env",
    "production": BASE_DIR / "configs/environments/production.env"
}
env_path = ENV_PATHS.get(ENV, ENV_PATHS["local"])  # fallback to local

# --- ADD DEBUGGING PRINTS HERE ---
print(f"DEBUG: ENV variable is: {ENV}")
print(f"DEBUG: Calculated env_path for Pydantic Settings: {env_path}")
print(f"DEBUG: Value of DB_USER from os.environ (before Pydantic): {os.getenv('DB_USER')}")
print(f"DEBUG: Value of DB_PASSWORD from os.environ (before Pydantic): {os.getenv('DB_PASSWORD')}")
# --- END DEBUGGING PRINTS ---

class Settings(BaseSettings):
    # Environment & App Settings
    ENV: Literal["local", "docker", "production"] = Field("local", env="ENV")
    ENVIRONMENT: Literal["dev", "staging", "production"] = Field("dev", env="ENVIRONMENT")
    DEBUG: bool = Field(False, env="DEBUG")
    APP_DEBUG: bool = Field(False, env="DEBUG")
    LOG_LEVEL: str = "INFO"
    LOG_ROTATION: str = "10 MB"
    LOG_BACKUP_COUNT: int = 5

    # Database Configuration
    DB_ENGINE: Literal["mysql", "postgresql"] = Field("mysql", env="DB_ENGINE")
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: SecretStr = Field(..., env="DB_PASSWORD")
    DB_HOST: str = Field("localhost", env="DB_HOST")
    DB_PORT: str = Field("3306", env="DB_PORT")
    DB_NAME: str = Field(..., env="DB_NAME")
    DB_POOL_SIZE: int = Field(5, env="DB_POOL_SIZE")
    DB_POOL_RECYCLE: int = Field(300, env="DB_POOL_RECYCLE")
    DB_MAX_OVERFLOW: int = 10

    # Security & Auth
    SECRET_KEY: SecretStr = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    TOKEN_ISSUER: str = Field("FinTrack", env="TOKEN_ISSUER")
    TOKEN_AUDIENCE: str = Field("FinTrack", env="TOKEN_AUDIENCE")

    # CORS
    CORS_ORIGINS: list[str] = Field(["*"], env="CORS_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=env_path,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> MySQLDsn | PostgresDsn:
        """Generate properly encoded DSN."""
        # --- ADD MORE DEBUGGING HERE ---
        print(f"DEBUG: DB_USER from Settings class: {self.DB_USER}")
        print(f"DEBUG: DB_PASSWORD from Settings class: {self.DB_PASSWORD.get_secret_value()}")
        print(f"DEBUG: DB_HOST from Settings class: {self.DB_HOST}")
        print(f"DEBUG: DB_NAME from Settings class: {self.DB_NAME}")
        # --- END DEBUGGING ---
        encoded_password = urllib.parse.quote_plus(self.DB_PASSWORD.get_secret_value())
        if self.DB_ENGINE == "mysql":
            return f"mysql+asyncmy://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        else:
            return f"postgresql+asyncpg://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def token_config(self) -> dict:
        return {
            "secret_key": self.SECRET_KEY.get_secret_value(),
            "algorithm": self.ALGORITHM,
            "access_expire": timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES),
            "refresh_expire": timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS),
            "issuer": self.TOKEN_ISSUER,
            "audience": self.TOKEN_AUDIENCE
        }

# Enum Definitions (unchanged)
class IncomeSource(str, Enum):
    SALARY = "Salary"
    FREELANCE = "Freelance"
    DIVIDEND = "Dividend"
    BONUS = "Bonus"
    INVESTMENT = "Investment"
    OTHER = "Other"

class IncomeFrequency(str, Enum):
    MONTHLY = "Monthly"
    WEEKLY = "Weekly"
    BIWEEKLY = "Biweekly"
    ONE_TIME = "One-time"

class Type(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    SAVINGS = "SAVINGS"

class PaymentMethod(str, Enum):
    CASH = "CASH"
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    MOBILE_PAYMENT = "MOBILE_PAYMENT"
    OTHER = "OTHER"

# Initialize settings
settings = Settings()