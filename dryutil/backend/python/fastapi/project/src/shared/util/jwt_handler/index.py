import os
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from jose import jwt, JWTError, ExpiredSignatureError

# Load env
load_dotenv()

# Keys (stored in base64 for cleaner .env)
PRIVATE_KEY = base64.b64decode(os.getenv("RSA_PRIVATE_KEY_BASE_64")).decode("utf-8")
PUBLIC_KEY = base64.b64decode(os.getenv("RSA_PUBLIC_KEY_BASE_64")).decode("utf-8")

# Config
ALGORITHM = os.getenv("JWT_ALGORITHM", "RS256")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))


class JWTHandler:
    @staticmethod
    def create_token(payload: Dict[str, Any], expire_minutes: Optional[int] = None) -> str:
        """Create JWT with expiration claim"""
        exp_time = datetime.utcnow() + timedelta(minutes=expire_minutes or EXPIRE_MINUTES)
        payload.update({"exp": exp_time})
        return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str, allow_expired: bool = False) -> Dict[str, Any]:
        """
        Decode JWT.
        - If `allow_expired=True`, expiration is ignored but other checks remain.
        """
        try:
            return jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
        except ExpiredSignatureError as e:
            if allow_expired:
                # Decode ignoring expiration
                return jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
            raise e
        except JWTError as e:
            raise e
