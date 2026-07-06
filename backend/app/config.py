from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "AutoClaims"
    debug: bool = True
    database_url: str = "sqlite:///./autoclaims.db"
    redis_url: Optional[str] = None

    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    qwen_model_max: str = "qwen3.7-max"
    qwen_model_plus: str = "qwen3.7-plus"
    qwen_model_flash: str = "qwen3.6-flash"

    human_review_threshold: float = 5000.0
    max_claim_images: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
