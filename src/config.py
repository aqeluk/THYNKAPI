from bson import ObjectId
from pydantic import AnyUrl, BaseSettings, EmailStr, validator

class AppSettings(BaseSettings):

    class Config:
        env_file = ".env"
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

    github_client_id: str
    github_client_secret: str
    github_redirect_uri: str
    github_scope: str
    github_server_base_url: str
    github_server_token_url: str
    github_server_userinfo_url: str

    microsoft_client_id: str
    microsoft_client_secret: str
    microsoft_redirect_uri: str
    microsoft_scope: str
    microsoft_server_base_url: str
    microsoft_server_token_url: str
    microsoft_server_userinfo_url: str

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    google_scope: str
    google_server_base_url: str
    google_server_token_url: str
    google_server_userinfo_url: str

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
