from pydantic import BaseSettings


class Settings(BaseSettings):
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_pass: str
    mysql_db: str

    class Config:
        env_file = ".env"