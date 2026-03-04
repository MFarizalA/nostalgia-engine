from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Alibaba Cloud Model Studio
    dashscope_api_key: str

    # Model names (configurable so they can be updated without code changes)
    qwen_model: str = "qwen-vl-max"
    wan_model:  str = "wan2.6-i2v-flash"

    # OSS
    oss_access_key_id:     str
    oss_access_key_secret: str
    oss_bucket_name:       str
    oss_endpoint:          str = "oss-cn-hangzhou.aliyuncs.com"
    oss_signed_url_expiry: int = 3600        # seconds

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
