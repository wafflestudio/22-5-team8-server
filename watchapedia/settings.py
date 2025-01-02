import os

from pydantic_settings import BaseSettings

ENV = os.getenv("ENV", "local") # 배포 시에는(merge) prod로 바꿔주세요
assert ENV in ("local", "prod")


class Settings(BaseSettings):
    @property
    def is_local(self) -> bool:
        return ENV == "local"

    @property
    def is_prod(self) -> bool:
        return ENV == "prod"

    @property
    def env_file(self) -> str:
        return f".env.{ENV}"

#SETTINGS 는 런타임에 변경되지 않으므로 미리 초기화해둡니다.
SETTINGS = Settings()