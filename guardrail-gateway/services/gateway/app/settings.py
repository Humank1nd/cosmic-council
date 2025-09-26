from pydantic import BaseModel
import os

class Settings(BaseModel):
    POSTGRES_DSN: str = (
        f"postgresql+psycopg://{os.getenv('POSTGRES_USER','guard')}:"
        f"{os.getenv('POSTGRES_PASSWORD','guardpw')}@{os.getenv('POSTGRES_HOST','postgres')}:"
        f"{os.getenv('POSTGRES_PORT','5432')}/{os.getenv('POSTGRES_DB','guard')}"
    )
    OPA_URL: str = os.getenv('OPA_URL','http://opa:8181/v1/data')

settings = Settings()
