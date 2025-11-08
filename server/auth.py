"""
Authentication và Authorization cho OTA Server
"""
import os
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Security, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
from pathlib import Path

# Security scheme
security = HTTPBearer()

# File lưu API keys và device tokens
AUTH_DIR = Path(__file__).parent.parent / "auth"
AUTH_DIR.mkdir(exist_ok=True)
API_KEYS_FILE = AUTH_DIR / "api_keys.json"
DEVICE_TOKENS_FILE = AUTH_DIR / "device_tokens.json"
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))

def load_api_keys():
    """Load API keys từ file"""
    if API_KEYS_FILE.exists():
        with open(API_KEYS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_api_keys(keys):
    """Lưu API keys vào file"""
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

def load_device_tokens():
    """Load device tokens từ file"""
    if DEVICE_TOKENS_FILE.exists():
        with open(DEVICE_TOKENS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_device_tokens(tokens):
    """Lưu device tokens vào file"""
    with open(DEVICE_TOKENS_FILE, 'w') as f:
        json.dump(tokens, f, indent=2)

def generate_api_key(name: str = "default") -> str:
    """Tạo API key mới"""
    api_key = secrets.token_urlsafe(32)
    keys = load_api_keys()
    keys[api_key] = {
        "name": name,
        "created_at": datetime.now().isoformat(),
        "last_used": None
    }
    save_api_keys(keys)
    return api_key

def verify_api_key(api_key: str) -> bool:
    """Xác minh API key"""
    keys = load_api_keys()
    if api_key in keys:
        # Cập nhật last_used
        keys[api_key]["last_used"] = datetime.now().isoformat()
        save_api_keys(keys)
        return True
    return False

def generate_device_token(device_id: str, expires_hours: int = 24 * 30) -> str:
    """Tạo JWT token cho device"""
    payload = {
        "device_id": device_id,
        "exp": datetime.utcnow() + timedelta(hours=expires_hours),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    
    # Lưu token vào file
    tokens = load_device_tokens()
    tokens[device_id] = {
        "token": token,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(hours=expires_hours)).isoformat()
    }
    save_device_tokens(tokens)
    
    return token

def verify_device_token(token: str) -> Optional[str]:
    """Xác minh device token và trả về device_id"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("device_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_api_key(api_key: str = Header(None, alias="X-API-Key")):
    """Middleware yêu cầu API key"""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Use header: X-API-Key"
        )
    
    if not verify_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return api_key

def require_device_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Middleware yêu cầu device token"""
    token = credentials.credentials
    device_id = verify_device_token(token)
    
    if not device_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired device token"
        )
    
    return device_id

def require_auth(api_key: Optional[str] = Header(None, alias="X-API-Key"),
                 credentials: Optional[HTTPAuthorizationCredentials] = Security(security, auto_error=False)):
    """Middleware linh hoạt: chấp nhận API key hoặc device token"""
    # Thử API key trước
    if api_key and verify_api_key(api_key):
        return {"type": "api_key", "value": api_key}
    
    # Thử device token
    if credentials:
        device_id = verify_device_token(credentials.credentials)
        if device_id:
            return {"type": "device_token", "device_id": device_id}
    
    raise HTTPException(
        status_code=401,
        detail="Authentication required. Use X-API-Key header or Bearer token"
    )

