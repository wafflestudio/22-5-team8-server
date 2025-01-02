from pydantic_settings import BaseSettings, SettingsConfigDict
from watchapedia.settings import SETTINGS  # 기존 SETTINGS를 가져옵니다.
from datetime import timedelta

class JWTSettings(BaseSettings):
    secret_key: str = ""
    algorithm: str = ""
    access_token_expires_minutes: int = 0
    refresh_token_expires_hours: int = 0

    @property
    def secret_key(self) -> str:
        return self.secret_key

    @property
    def algorithm(self) -> str:
        return self.algorithm
    
    @property
    def access_token_expires_minutes(self) -> int:
        return self.access_token_expires_minutes
    
    @property
    def refresh_token_expires_hours(self) -> int:
        return self.refresh_token_expires_hours

    model_config = SettingsConfigDict(
        case_sensitive=False, # 대소문자 구분 X
        env_prefix="JWT_",  # JWT_로 시작하는 환경변수만 사용
        env_file=SETTINGS.env_file,  # SETTINGS에서 env_file 경로를 사용
        extra="ignore",  # 추가적인 환경변수는 무시
    )

JWT_SETTINGS = JWTSettings()
print(JWT_SETTINGS.access_token_expires_minutes)
print(JWT_SETTINGS.refresh_token_expires_hours)