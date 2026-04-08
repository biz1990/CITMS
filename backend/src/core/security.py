from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import hmac
import hashlib
from backend.src.core.config import settings

# Using Argon2id for user passwords
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7) # Refresh token lasts 7 days
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_agent_token_hash(token: str) -> str:
    """Compute HMAC-SHA256 for agent tokens as per CITMS 3.6 Spec."""
    return hmac.new(
        settings.AGENT_SECRET_KEY.encode(),
        token.encode(),
        hashlib.sha256
    ).hexdigest()
