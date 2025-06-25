from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from auth.auth_service import AuthService, get_auth_service
from auth.jwt_service import JwtService, get_jwt_service
from common.schema import ApiResponse
from user.schema import UserRegister, UserLogin
from user.service import UserService, get_user_service
from util.decorators import with_api_exception_handling

router = APIRouter()


@router.post("/register", response_model=ApiResponse)
@with_api_exception_handling
def register(entity: UserRegister,
             user_service: UserService = Depends(get_user_service)):
    return ApiResponse(status=HTTPStatus.CREATED,
                       data=user_service.create(entity))


@router.post("/login", response_model=ApiResponse)
@with_api_exception_handling
def login(response: Response,
          entity: UserLogin,
          auth_service: AuthService = Depends(get_auth_service),
          jwt_service: JwtService = Depends(get_jwt_service)):
    result = auth_service.authenticate_user(entity.email, entity.password)
    if not result:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Incorrect email or password")

    token = jwt_service.create_access_token(
        subject=result.id,
        payload={
            "id": result.id,
            "email": result.email,
            "username": result.username,
            "is_admin": result.is_admin,
        }
    )
    response.set_cookie(key="Authorization", value=f"{token}", httponly=True)
    return ApiResponse(status=HTTPStatus.OK, data={"token": token})
