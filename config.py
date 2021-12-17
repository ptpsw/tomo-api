from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    cors_origins: List[str]
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_pass: str
    mysql_db: str

    class Config:
        env_file = ".env"