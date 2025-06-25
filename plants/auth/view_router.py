from fastapi import APIRouter, Request, Depends
from starlette.responses import Response, RedirectResponse
from starlette.templating import Jinja2Templates

from auth.auth_service import AuthService, get_auth_service, get_principal
from auth.jwt_service import get_jwt_service, JwtService
from user.schema import UserLogin, UserRegister
from user.service import UserService, get_user_service

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login")
def login(request: Request,
          principal=Depends(get_principal)):
    if principal:
        return RedirectResponse("/plants")

    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "principal": principal
    })


@router.get("/register")
def register(request: Request,
             principal=Depends(get_principal)):
    if principal:
        return RedirectResponse("/plants")

    return templates.TemplateResponse("auth/register.html", {
        "request": request,
        "principal": principal
    })


@router.post("/try-login")
def try_login(request: Request,
              response: Response,
              entity: UserLogin,
              auth_service: AuthService = Depends(get_auth_service),
              jwt_service: JwtService = Depends(get_jwt_service),
              principal=Depends(get_principal)):
    if principal:
        response.headers["HX-Redirect"] = "/plants"
        return {}

    result = auth_service.authenticate_user(entity.email, entity.password)
    if not result:
        return templates.TemplateResponse("auth/auth_error.html", {
            "request": request,
            "detail": "Wrong email or password"
        })

    token = jwt_service.create_access_token(
        subject=result.id,
        payload={
            "id": result.id,
            "email": result.email,
            "username": result.username,
            "is_admin": result.is_admin,
        }
    )
    response.set_cookie(key="Authorization", value=f"{token}", httponly=False)
    response.headers["HX-Redirect"] = "/plants"
    return {}


@router.post("/try-register")
def try_register(entity: UserRegister,
                 request: Request,
                 response: Response,
                 auth_service: AuthService = Depends(get_auth_service),
                 user_service: UserService = Depends(get_user_service),
                 jwt_service: JwtService = Depends(get_jwt_service),
                 principal=Depends(get_principal)):
    if principal:
        response.headers["HX-Redirect"] = "/plants"
        return {}

    result = user_service.create(entity)
    if not result:
        return templates.TemplateResponse("auth/auth_error.html", {
            "request": request,
            "detail": "Could not register"
        })

    token = jwt_service.create_access_token(
        subject=result.id,
        payload={
            "id": result.id,
            "email": result.email,
            "username": result.username,
            "is_admin": result.is_admin,
        }
    )
    response.set_cookie(key="Authorization", value=f"{token}", httponly=False)
    response.headers["HX-Redirect"] = "/plants"
    return {}
