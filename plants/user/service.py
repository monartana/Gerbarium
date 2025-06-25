from http import HTTPStatus

from fastapi import Depends, HTTPException
from typing import Optional

from auth.password_service import get_password_service, PasswordService
from user.repository import UserRepository, get_user_repository
from user.schema import UserRegister, UserUpdate, UserRead
from util.decorators import with_error_logger


class UserService:
    def __init__(self,
                 repo: Depends(get_user_repository),
                 password_service: PasswordService) -> None:
        self.user_repository = repo
        self.password_service = password_service

    @with_error_logger
    def get_by_id(self, user_id: int):
        db_user = self.user_repository.get_by_id(user_id)

        if db_user is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"User with id: {user_id} not found")

        return UserRead.from_orm(db_user)

    def check_exists(self, email: str, username: str):
        db_user = self.user_repository.get_by_email(email)
        if db_user:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail=f"User with email: {email} already exists")

        db_user = self.user_repository.get_by_username(username)
        if db_user:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail=f"User with username: {username} already exists")

    @with_error_logger
    def create(self, entity: UserRegister):
        self.check_exists(entity.email, entity.username)

        entity.password = self.password_service.get_hash_password(entity.password)
        db_user = self.user_repository.create(entity)
        return UserRead.from_orm(db_user)

    @with_error_logger
    def replacement_update(self,
                           user_id: int,
                           user_update: UserUpdate):
        self.check_exists(user_update.email, user_update.username)
        db_user = self.user_repository.update(user_id, user_update)

        if db_user is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"User with id: {user_id} not found")

        return UserRead.from_orm(db_user)

    @with_error_logger
    def patch_update(self,
                     user_id: int,
                     user_update: UserUpdate):
        self.check_exists(user_update.email, user_update.username)

        db_user = self.user_repository.get_by_id(user_id)

        if db_user is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"User with id: {user_id} not found")

        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, field, value)

        db_user = self.user_repository.update(user_id, db_user)

        return UserRead.from_orm(db_user)

    @with_error_logger
    def delete(self, item_id: int):
        db_user = self.user_repository.delete(item_id)
        return UserRead.from_orm(db_user)


def get_user_service(repo: UserRepository = Depends(get_user_repository),
                     password_service=Depends(get_password_service)):
    return UserService(repo, password_service)
