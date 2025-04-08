from pydantic_settings import BaseSettings 

class Settings(BaseSettings):
    environment: str = "production"
    database_url: str

    # JWT Auth Config
    secret_key: str = "shrinkr-dev-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # # Optional: add these later
    # redis_url: str = "redis://localhost:6379/0"
    # kafka_bootstrap_servers: str = "localhost:9092"
    # kafka_topic: str = "clickstream"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()