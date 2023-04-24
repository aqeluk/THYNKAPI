from pydantic import BaseSettings, EmailStr
import os


class SASettings(BaseSettings):

    class Config:
        env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
        env_file_encoding = "utf-8"
        env_prefix = "sa_"

    sas_email: EmailStr
    sas_pass: str
    google_chrome_bin: str
    chromedriver_path:str


sa_settings = SASettings()
