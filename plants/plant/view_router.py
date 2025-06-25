import datetime

import timeago
from fastapi import APIRouter, Depends, Request, Query
from starlette.templating import Jinja2Templates

from auth.auth_service import get_principal
from plant.service import PlantService, get_plant_service

router = APIRouter()
templates = Jinja2Templates(directory="templates")

PAGE_SIZE = 12


@router.get("/")
def plant_list(request: Request,
               query: str = Query(default=None),
               sort_by: str = Query(default=None),
               page_size: int = Query(default=PAGE_SIZE),
               page_number: int = Query(default=1),
               plant_service: PlantService = Depends(get_plant_service),
               principal=Depends(get_principal)):
    data = plant_service.fetch(page_size, page_number, query, sort_by)
    return templates.TemplateResponse("plant/plant-list.html",
                                      {
                                          "request": request,
                                          "plants": data.items,
                                          "total": data.total_pages,
                                          "current": data.current_page,
                                          "principal": principal
                                      })


@router.get("/fragments/plant-list")
def plant_list_fragment(request: Request,
                        query: str = Query(default=None),
                        sort_by: str = Query(default=None),
                        page_size: int = Query(default=PAGE_SIZE),
                        page_number: int = Query(default=1),
                        plant_service: PlantService = Depends(get_plant_service),
                        principal=Depends(get_principal)):
    data = plant_service.fetch(page_size, page_number, query, sort_by)
    return templates.TemplateResponse("plant/fragments/plant-list-fragment.html",
                                      {
                                          "request": request,
                                          "plants": data.items,
                                          "total": data.total_pages,
                                          "current": data.current_page,
                                          "principal": principal
                                      })


@router.get("/{plant_id}")
def plant(plant_id: int,
          request: Request,
          plant_service: PlantService = Depends(get_plant_service),
          principal=Depends(get_principal)):
    now = datetime.datetime.now()
    data = plant_service.get_by_id(plant_id)
    data.comments.sort(key=lambda x: x.created_at, reverse=True)
    for comment in data.comments:
        comment.created_at = timeago.format(comment.created_at, now)

    # Get similar plants
    similar_plants = plant_service.get_similar_plants(plant_id, limit=8)
    
    # Get personalized recommendations if user is logged in
    personalized_recommendations = []
    if principal and principal['id']:
        personalized_recommendations = plant_service.get_personalized_recommendations(principal['id'], limit=8)

    return templates.TemplateResponse("plant/plant.html", {
        "request": request,
        "plant": data,
        "principal": principal,
        "similar_plants": similar_plants,
        "personalized_recommendations": personalized_recommendations
    })
