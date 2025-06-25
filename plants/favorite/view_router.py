from fastapi import APIRouter, Depends, Query
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from favorite.schema import FavoriteCreate
from favorite.service import FavoriteService, get_favorite_service
from common.schema import ApiResponse
from auth.filter import with_auth
from templates.const import ALERT_TYPE
from plant.service import PlantService, get_plant_service

router = APIRouter()
templates = Jinja2Templates(directory="templates")

PAGE_SIZE = 12


@router.get("/my", response_model=ApiResponse)
def favorites_view(request: Request,
                   page_size: int = Query(default=PAGE_SIZE),
                   page_number: int = Query(default=1),
                   favorite_service: FavoriteService = Depends(get_favorite_service),
                   plant_service: PlantService = Depends(get_plant_service),
                   principal=Depends(with_auth(admin_only=False))):
    data = favorite_service.fetch_by_user_id(principal['id'], page_size, page_number)
    plants = list(map(lambda x: x.plant, data.items))
    
    # Get personalized recommendations based on user's interactions
    personalized_recommendations = plant_service.get_personalized_recommendations(principal['id'], limit=8)

    return templates.TemplateResponse("favorite/favorite-list.html",
                                      {
                                          "request": request,
                                          "plants": plants,
                                          "total": data.total_pages,
                                          "current": data.current_page,
                                          "principal": principal,
                                          "personalized_recommendations": personalized_recommendations
                                      })


@router.get("/my/fragments/favorite-list")
def favorites_fragment_view(request: Request,
                            page_size: int = Query(default=PAGE_SIZE),
                            page_number: int = Query(default=1),
                            favorite_service: FavoriteService = Depends(get_favorite_service),
                            principal=Depends(with_auth(admin_only=False))):
    data = favorite_service.fetch_by_user_id(principal['id'], page_size, page_number)
    plants = list(map(lambda x: x.plant, data.items))

    return templates.TemplateResponse("favorite/fragments/favorite-list-fragment.html",
                                      {
                                          "request": request,
                                          "plants": plants,
                                          "total": data.total_pages,
                                          "current": data.current_page,
                                          "principal": principal
                                      })


@router.post("/{plant_id}", response_model=ApiResponse)
def toggle(request: Request,
           plant_id: int,
           favorite_service: FavoriteService = Depends(get_favorite_service),
           principal=Depends(with_auth(admin_only=False))):
    data = favorite_service.toggle(FavoriteCreate(
        user_id=principal['id'],
        plant_id=plant_id,
    ))

    if hasattr(data, "plant"):
        msg = "Added to favorites"
    else:
        msg = "Removed from favorites"

    return templates.TemplateResponse("components/ui/alert.html",
                                      {
                                          "request": request,
                                          "msg": msg,
                                          "cls": ALERT_TYPE["success"],
                                          "principal": principal
                                      })
