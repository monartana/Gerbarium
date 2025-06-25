from fastapi import Depends
from fastapi.security import HTTPBearer
from starlette.requests import Request

from auth.jwt_service import JwtService, get_jwt_service
from auth.password_service import PasswordService, get_password_service
from user.repository import UserRepository, get_user_repository

security_scheme = HTTPBearer()


class AuthService:
    def __init__(self,
                 password_service: PasswordService,
                 user_repository: UserRepository):
        self.password_service = password_service
        self.user_repository = user_repository

    def authenticate_user(self, email, password):
        db_user = self.user_repository.get_by_email(email)
        if not db_user:
            return None

        if not self.password_service.verify_password(password, db_user.password):
            return None

        return db_user


def get_principal(req: Request,
                  jwt_service: JwtService = Depends(get_jwt_service)):
    header_token = req.headers.get('Authorization')
    cookie_token = req.cookies.get('Authorization')

    if header_token:
        return jwt_service.decode_token(header_token)

    if cookie_token:
        return jwt_service.decode_token(cookie_token)

    return None


def get_auth_service(password_service=Depends(get_password_service),
                     user_repository=Depends(get_user_repository)):
    return AuthService(password_service, user_repository)
