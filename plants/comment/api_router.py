from http import HTTPStatus

from fastapi import APIRouter, Depends, Query

from comment.schema import CommentCreate, CommentCreateRequest
from comment.service import CommentService, get_comment_service
from common.schema import ApiResponse
from util.decorators import with_api_exception_handling
from auth.filter import with_auth

router = APIRouter()


@router.get("/", response_model=ApiResponse)
@with_api_exception_handling
def fetch(query: str = Query(default=None),
          sort_by: str = Query(default=None),
          page_size: int = Query(default=10),
          page_number: int = Query(default=1),
          comment_service: CommentService = Depends(get_comment_service)):
    data = comment_service.fetch(page_size, page_number, query, sort_by)
    return ApiResponse(status=HTTPStatus.OK, data=data)


@router.get("/{comment_id}", response_model=ApiResponse)
@with_api_exception_handling
def get_by_id(comment_id: int,
              comment_service: CommentService = Depends(get_comment_service)):
    data = comment_service.get_by_id(comment_id)
    return ApiResponse(status=HTTPStatus.OK, data=data)


@router.post("/", response_model=ApiResponse)
@with_api_exception_handling
def create(entity: CommentCreateRequest,
           comment_service: CommentService = Depends(get_comment_service),
           user=Depends(with_auth(admin_only=False))):
    create_data = CommentCreate(
        user_id=user['id'],
        plant_id=entity.plant_id,
        text=entity.text,
    )

    data = comment_service.create(create_data)
    return ApiResponse(status=HTTPStatus.CREATED, data=data)
