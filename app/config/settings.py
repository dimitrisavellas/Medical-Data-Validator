from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(..., env='DATABASE_URL')
    log_level: str = Field("INFO", env='LOG_LEVEL')
    environment: str = Field("production", env='ENVIRONMENT')
    log_file_path: str = Field("/logs/app.log", env='LOG_FILE_PATH')
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
