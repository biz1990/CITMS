import base64
import os
from datetime import datetime, timedelta
from typing import Any, Union

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

# --- AES-256-GCM Encryption for sensitive data (Module 2, 5.2) ---

def _get_aes_key() -> bytes:
    # Use the first 32 bytes of SECRET_KEY for AES-256
    key = settings.SECRET_KEY.encode()
    if len(key) < 32:
        return key.ljust(32, b"0")
    return key[:32]

import hmac
import hashlib

def encrypt_data(plain_text: str) -> str:
    if not plain_text:
        return ""
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plain_text.encode(), None)
    # Store as base64(nonce + ciphertext)
    return base64.b64encode(nonce + ct).decode()

def decrypt_data(encrypted_data: str) -> str:
    if not encrypted_data:
        return ""
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    try:
        data = base64.b64decode(encrypted_data)
        nonce = data[:12]
        ct = data[12:]
        return aesgcm.decrypt(nonce, ct, None).decode()
    except Exception:
        return "[ENCRYPTION_ERROR]"

# --- HMAC-SHA256 for Agent Identification (Module 1, 9.5) ---

def hash_agent_token(token: str) -> str:
    """v3.6 §1.4 & §9.5: Fast HMAC-SHA256 for high-speed packet validation."""
    if not token:
        return ""
    # System_secret used as key for HMAC
    key = settings.SECRET_KEY.encode()
    return hmac.new(key, token.encode(), hashlib.sha256).hexdigest()

def verify_agent_token(token: str, known_hash: str) -> bool:
    """Compute HMAC of incoming token and compare with stored hash securely."""
    if not token or not known_hash:
        return False
    computed_hash = hash_agent_token(token)
    return hmac.compare_digest(computed_hash, known_hash)
