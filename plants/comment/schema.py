from typing import List

from pydantic import Field

from common.schema import TimestampMixin, OrmBase
from user.schema import UserRead


class CommentBase(OrmBase):
    text: str = Field(min_length=1, max_length=255)


class CommentRead(CommentBase, TimestampMixin):
    id: int
    user: UserRead


class CommentList(OrmBase):
    items: List[CommentRead]


class CommentCreateRequest(CommentBase):
    plant_id: int


class CommentCreate(CommentCreateRequest):
    user_id: int


class CommentUpdate(CommentBase):
    pass
