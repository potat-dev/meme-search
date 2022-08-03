from pydantic import BaseSettings

class Settings(BaseSettings):
  mongo_uri: str
  mongo_db: str
  mongo_collection: str

settings = Settings(
  _env_file='settings.env',
  _env_file_encoding='utf-8'
)