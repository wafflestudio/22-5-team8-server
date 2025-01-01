from datetime import datetime, timedelta
from auth.settings import JWT_SETTINGS
from jose.exceptions import JWTError, ExpiredSignatureError
from watchapedia.common.errors import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: int):
    # data를 받아서 JWT access 토큰을 생성
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=expires_delta)
    to_encode.update({'exp': expire})
    to_encode.update({'typ': 'access'})
    encoded_jwt = jwt.encode(to_encode, JWT_SETTINGS.secret_key, algorithm=JWT_SETTINGS.algorithm)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: int):
    # data를 받아서 JWT refresh 토큰을 생성
    to_encode = data.copy()
    expire = datetime.now() + timedelta(hours=expires_delta)
    to_encode.update({'exp': expire})
    to_encode.update({'typ': 'refresh'})
    encoded_jwt = jwt.encode(to_encode, JWT_SETTINGS.secret_key, algorithm=JWT_SETTINGS.algorithm)
    return encoded_jwt

def decode_token(token: str):
    # token을 받아서 payload를 반환
    try:
        payload = jwt.decode(token, JWT_SETTINGS.secret_key, algorithms=JWT_SETTINGS.algorithm, options={"require": ["sub"]})
        return payload
    except jwt.ExpiredSignatureError:
        raise ExpiredSignatureError()
    except jwt.InvalidTokenError:
        raise InvalidTokenError()
    
def create_hashed_password(password: str):
    # password를 받아서 bcrypt로 암호화
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    # plain_password와 hashed_password를 받아서 일치하는지 확인
    return pwd_context.verify(plain_password, hashed_password)