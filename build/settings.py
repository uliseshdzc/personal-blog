from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", str_to_lower=True)
    service_account_key: dict
    blog_folder_id: str