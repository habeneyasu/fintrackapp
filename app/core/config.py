from datetime import timedelta
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, MySQLDsn, PostgresDsn, SecretStr
from pathlib import Path
import urllib.parse
from typing import Literal
from enum import Enum


BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # Database Configuration
    ENV: str = "dev" 

    DB_ENGINE: Literal["mysql", "postgresql"] = Field("mysql", env="DB_ENGINE")
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    DB_HOST: str = Field("localhost", env="DB_HOST")
    DB_PORT: str = Field("3306", env="DB_PORT")
    DB_NAME: str = Field(..., env="DB_NAME")
    DB_POOL_SIZE: int = Field(5, env="DB_POOL_SIZE")
    DB_POOL_RECYCLE: int = Field(300, env="DB_POOL_RECYCLE")
    DB_MAX_OVERFLOW: int = 10 

    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    TOKEN_ISSUER: str = Field("FinTrack", env="TOKEN_ISSUER")
    TOKEN_AUDIENCE: str = Field("FinTrack", env="TOKEN_AUDIENCE")

    CORS_ORIGINS: list[str] = Field(["*"], env="CORS_ORIGINS")


    # Security Configuration
    SECRET_KEY: SecretStr = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # App Configuration
    DEBUG: bool = Field(False, env="APP_DEBUG")
    ENVIRONMENT: Literal["dev", "staging", "production"] = Field("dev", env="ENVIRONMENT")


    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    LOG_ROTATION: str = "10 MB"
    LOG_BACKUP_COUNT: int = 5
    APP_DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> MySQLDsn | PostgresDsn:
        """Generate properly encoded DSN"""
        encoded_password = urllib.parse.quote_plus(self.DB_PASSWORD)
        
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

settings = Settings()
