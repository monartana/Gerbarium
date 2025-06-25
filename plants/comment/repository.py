from fastapi import Depends
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from database import get_db

from comment.model import Comment
from comment.schema import CommentCreate, CommentUpdate


class CommentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self,
                  comment_id: int):
        return (self.session.query(Comment)
                .filter(Comment.id == comment_id).first())

    def fetch_by_plant_id(self,
                          plant_id: int,
                          sort_direction: str):
        query = self.session.query(Comment).filter(Comment.plant_id == plant_id)

        ordering = desc(Comment.id) if sort_direction == 'desc' else asc(Comment.id)
        query = query.order_by(ordering)

        return query.all()

    def create(self, entity: CommentCreate):
        db_comment = Comment(**entity.model_dump())

        self.session.add(db_comment)
        self.session.commit()
        self.session.refresh(db_comment)

        return db_comment

    def update(self,
               comment_id: int,
               comment_update: CommentUpdate):
        db_comment = self.get_by_id(comment_id)
        if not db_comment:
            return None

        for var, value in vars(comment_update).items():
            setattr(db_comment, var, value)

        self.session.commit()
        self.session.refresh(db_comment)

        return db_comment

    def delete(self, item_id: int):
        db_comment = self.get_by_id(item_id)

        if not db_comment:
            return None

        self.session.delete(db_comment)
        self.session.commit()

        return db_comment


def get_comment_repository(db: Session = Depends(get_db)):
    return CommentRepository(db)
