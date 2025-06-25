from http import HTTPStatus

from fastapi import Depends, HTTPException

from auth.auth_service import get_principal


def with_auth(admin_only: bool):
    def validate(current_user=Depends(get_principal)):
        if not current_user:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                detail="Not authenticated")

        if not current_user['is_admin'] and admin_only:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                detail="Not enough privileges")

        return current_user

    return validate


def guest_only():
    def validate(current_user=Depends(get_principal)):
        if current_user:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                detail="Trying to access guest only route")

        return current_user

    return validate
