from http import HTTPStatus

from fastapi import APIRouter, Depends, Query

from favorite.schema import FavoriteCreate
from favorite.service import FavoriteService, get_favorite_service
from common.schema import ApiResponse
from util.decorators import with_api_exception_handling
from auth.filter import with_auth

router = APIRouter()


@router.get("/my", response_model=ApiResponse)
@with_api_exception_handling
def favorites(page_size: int = Query(default=10),
              page_number: int = Query(default=1),
              favorite_service: FavoriteService = Depends(get_favorite_service),
              user=Depends(with_auth(admin_only=False))):
    data = favorite_service.fetch_by_user_id(user['id'], page_size, page_number)
    return ApiResponse(status=HTTPStatus.CREATED, data=data)


@router.post("/{plant_id}", response_model=ApiResponse)
@with_api_exception_handling
def toggle(plant_id: int,
           favorite_service: FavoriteService = Depends(get_favorite_service),
           user=Depends(with_auth(admin_only=False))):
    data = FavoriteCreate(
        user_id=user['id'],
        plant_id=plant_id,
    )

    return ApiResponse(status=HTTPStatus.CREATED, data=favorite_service.toggle(data))
