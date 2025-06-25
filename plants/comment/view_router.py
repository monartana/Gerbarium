from datetime import datetime

import timeago
from fastapi import APIRouter, Request, Query, Depends
from starlette.templating import Jinja2Templates

from auth.auth_service import get_principal
from auth.filter import with_auth
from comment.schema import CommentCreateRequest, CommentCreate
from comment.service import get_comment_service, CommentService
from templates.const import ALERT_TYPE

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/fragments/{plant_id}")
def get(request: Request,
        plant_id: int,
        sort_direction: str = Query(default="asc"),
        comment_service: CommentService = Depends(get_comment_service),
        principal=Depends(get_principal)):
    data = comment_service.fetch_by_plant_id(plant_id, sort_direction)
    now = datetime.now()
    for comment in data.items:
        comment.created_at = timeago.format(comment.created_at, now)
    return templates.TemplateResponse("comment/fragments/comment-list.html",
                                      {
                                          "request": request,
                                          "comments": data.items,
                                          "principal": principal
                                      })


@router.post("/")
def create(request: Request,
           entity: CommentCreateRequest,
           comment_service: CommentService = Depends(get_comment_service),
           principal=Depends(with_auth(admin_only=False))):
    data = CommentCreate(
        user_id=principal['id'],
        plant_id=entity.plant_id,
        text=entity.text,
    )
    _ = comment_service.create(data)

    return templates.TemplateResponse("components/ui/alert.html", {
        "request": request,
        "type": "success",
        "msg": "Your has been comment created",
        "cls": ALERT_TYPE["success"],
        "principal": principal
    })
