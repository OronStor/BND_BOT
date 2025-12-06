from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DISCORD_TOKEN: str
    YANDEX_MUSIC_TOKEN: str

settings = Settings()