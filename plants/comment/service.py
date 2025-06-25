from http import HTTPStatus

from fastapi import Depends, HTTPException

from comment.repository import CommentRepository, get_comment_repository
from comment.schema import CommentCreate, CommentUpdate, CommentRead, CommentList
from util.decorators import with_error_logger


class CommentService:
    def __init__(self, repo: CommentRepository) -> None:
        self.comment_repository = repo

    @with_error_logger
    def get_by_id(self, comment_id: int):
        db_comment = self.comment_repository.get_by_id(comment_id)

        if db_comment is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail=f"Comment with id: {comment_id} not found")

        return CommentRead.from_orm(db_comment)

    @with_error_logger
    def fetch_by_plant_id(self,
                          plant_id: int,
                          sort_direction: str):
        db_comments = self.comment_repository.fetch_by_plant_id(plant_id,
                                                                sort_direction)
        return CommentList.from_orm({"items": db_comments})

    @with_error_logger
    def create(self, entity: CommentCreate):
        db_comment = self.comment_repository.create(entity)
        return CommentRead.from_orm(db_comment)

    @with_error_logger
    def replacement_update(self,
                           comment_id: int,
                           comment_update: CommentUpdate):
        db_comment = self.comment_repository.update(comment_id, comment_update)

        if db_comment is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail=f"Comment with id: {comment_id} not found")

        return CommentRead.from_orm(db_comment)

    @with_error_logger
    def patch_update(self,
                     comment_id: int,
                     comment_update: CommentUpdate):
        db_comment = self.comment_repository.get_by_id(comment_id)

        if db_comment is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail=f"Comment with id: {comment_id} not found")

        for field, value in comment_update.dict(exclude_unset=True).items():
            setattr(db_comment, field, value)

        db_comment = self.comment_repository.update(comment_id, db_comment)

        return CommentRead.from_orm(db_comment)

    @with_error_logger
    def delete(self, item_id: int):
        db_comment = self.comment_repository.delete(item_id)
        return CommentRead.from_orm(db_comment)


def get_comment_service(repo: CommentRepository = Depends(get_comment_repository)):
    return CommentService(repo)
