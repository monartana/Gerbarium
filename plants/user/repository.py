from fastapi import Depends
from sqlalchemy.orm import Session

from database import get_db

from user.model import User
from user.schema import UserRegister, UserUpdate


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: int):
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_email(self, user_email: str):
        return self.session.query(User).filter(User.email == user_email).first()

    def get_by_username(self, user_username: str):
        return self.session.query(User).filter(User.username == user_username).first()

    def create(self, entity: UserRegister):
        db_user = User(**entity.model_dump())

        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)

        return db_user

    def update(self,
               user_id: int,
               user_update: UserUpdate):
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        for var, value in vars(user_update).items():
            setattr(db_user, var, value)

        self.session.commit()
        self.session.refresh(db_user)

        return db_user

    def delete(self, item_id: int):
        db_user = self.get_by_id(item_id)

        if not db_user:
            return None

        self.session.delete(db_user)
        self.session.commit()

        return db_user


def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db)
