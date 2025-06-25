from http import HTTPStatus

from fastapi import APIRouter, Depends, Query

from comment.service import CommentService, get_comment_service
from plant.schema import PlantCreate, PlantUpdate
from plant.service import PlantService, get_plant_service
from common.schema import ApiResponse
from util.decorators import with_api_exception_handling
from auth.filter import with_auth

router = APIRouter()


@router.get("/", response_model=ApiResponse)
@with_api_exception_handling
def fetch(query: str = Query(default=None),
          sort_by: str = Query(default=None),
          sort_direction: str = Query(default="asc"),
          page_size: int = Query(default=10),
          page_number: int = Query(default=1),
          plant_service: PlantService = Depends(get_plant_service)):
    data = plant_service.fetch(
        page_size, page_number, query, sort_by, sort_direction)
    return ApiResponse(status=HTTPStatus.OK, data=data)


@router.get("/{plant_id}", response_model=ApiResponse)
@with_api_exception_handling
def get_by_id(plant_id: int,
              plant_service: PlantService = Depends(get_plant_service)):
    data = plant_service.get_by_id(plant_id)
    return ApiResponse(status=HTTPStatus.OK, data=data)


@router.get("/{plant_id}/comments", response_model=ApiResponse)
@with_api_exception_handling
def fetch_by_plant_id(plant_id: int,
                      sort_by: str = Query(default=None),
                      page_size: int = Query(default=10),
                      page_number: int = Query(default=1),
                      comment_service: CommentService = Depends(get_comment_service)):
    data = comment_service.fetch_by_plant_id(
        plant_id, page_size, page_number, sort_by)
    return ApiResponse(status=HTTPStatus.OK, data=data)


@router.post("/", response_model=ApiResponse)
@with_api_exception_handling
def create(entity: PlantCreate,
           plant_service: PlantService = Depends(get_plant_service),
           _=Depends(with_auth(admin_only=True))):
    return ApiResponse(status=HTTPStatus.CREATED, data=plant_service.create(entity))


@router.put("/{plant_id}", response_model=ApiResponse)
@with_api_exception_handling
def replace(plant_id: int,
            entity: PlantUpdate,
            plant_service: PlantService = Depends(get_plant_service),
            _=Depends(with_auth(admin_only=True))):
    return ApiResponse(status=HTTPStatus.OK, data=plant_service.replacement_update(plant_id, entity))


@router.patch("/{plant_id}", response_model=ApiResponse)
@with_api_exception_handling
def patch(plant_id: int,
          entity: PlantUpdate,
          plant_service: PlantService = Depends(get_plant_service),
          _=Depends(with_auth(admin_only=True))):
    return ApiResponse(status=HTTPStatus.OK, data=plant_service.patch_update(plant_id, entity))


@router.delete("/{plant_id}", response_model=ApiResponse)
@with_api_exception_handling
def delete(plant_id: int,
           plant_service: PlantService = Depends(get_plant_service),
           _=Depends(with_auth(admin_only=True))):
    return ApiResponse(status=HTTPStatus.OK, data=plant_service.delete(plant_id))
