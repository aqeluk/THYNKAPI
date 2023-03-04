from bson import ObjectId
from pydantic import AnyUrl, BaseSettings, EmailStr, validator


class AppSettings(BaseSettings):

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        env_prefix = "app_"

    mongodb_url: AnyUrl
    postgresql_url: AnyUrl
    mail_username: EmailStr
    mail_password: str
    secret_key: str
    mail_from: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    algorithm: str

    @property
    def db_uri(self) -> str:
        return self.postgresql_url

    @validator('MAIL_PORT', pre=True)
    def cast_mail_port(cls, v):
        return int(v)


class CommonConfig:
    arbitrary_types_allowed = True
    json_encoders = {ObjectId: str}


settings = AppSettings()
