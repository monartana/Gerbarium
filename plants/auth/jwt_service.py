from datetime import datetime, timedelta
from typing import Any

from jose import jwt

from util.decorators import with_error_logger


class JwtService:
    ALGORITHM = 'HS256'
    SECRET_KEY = '0auFzYdG8EOOx0a4YEL9a19J0eW-I9z-7eWCaAJ-mO1cZkIDFaQQtHbPX0uXPqgEp_JajdKMZg8zFs05nxNEOg'
    ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 hours

    @with_error_logger
    def decode_token(self, token):
        try:
            data = jwt.decode(token,
                              self.SECRET_KEY, algorithms=self.ALGORITHM)
            return data['payload']
        except Exception:
            return None

    @with_error_logger
    def create_access_token(self,
                            subject: str,
                            payload: Any,
                            expires_delta: timedelta = None):
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode = {"exp": expire, "sub": str(subject), "payload": payload}
        encoded_jwt = jwt.encode(to_encode,
                                 self.SECRET_KEY, algorithm=self.ALGORITHM)

        return encoded_jwt


def get_jwt_service():
    return JwtService()
