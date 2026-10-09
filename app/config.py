from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./points_reward.db"
    SECRET_KEY: str = "points-reward-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 天
    UPLOAD_DIR: str = "uploads"
    MAX_IMAGE_SIZE_MB: int = 2

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()

# 确保上传目录存在
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
