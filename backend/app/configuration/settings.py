from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "CTX OData Explorer"
    app_version: str = "1.0.0"
    debug: bool = False

    ctx_data_source: str = Field(default="seed")
    capm_odata_base_url: str = Field(default="")
    capm_odata_username: str = Field(default="")
    capm_odata_password: str = Field(default="")

    cors_origins: str = Field(default="http://localhost:5173")

    seed_data_dir: str = Field(default="database/ctx/seed_data")


settings = Settings()
