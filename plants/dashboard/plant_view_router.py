import datetime

import timeago
from fastapi import APIRouter, Depends, Request, Query
from starlette.templating import Jinja2Templates

from auth.auth_service import get_principal
from auth.filter import with_auth
from plant.schema import PlantCreate, PlantUpdate
from plant.service import PlantService, get_plant_service
from templates.const import ALERT_TYPE

router = APIRouter()
templates = Jinja2Templates(directory="templates")

PAGE_SIZE = 12


@router.get("/")
def plant_table(request: Request,
                query: str = Query(default=None),
                sort_by: str = Query(default="id"),
                sort_direction: str = Query(default="desc"),
                page_size: int = Query(default=PAGE_SIZE),
                page_number: int = Query(default=1),
                plant_service: PlantService = Depends(get_plant_service),
                principal=Depends(with_auth(admin_only=True))):
    data = plant_service.fetch(page_size, page_number, query, sort_by, sort_direction)
    return templates.TemplateResponse("dashboard/plant/plant_table.html", {
        "request": request,
        "plants": data.items,
        "total": data.total_pages,
        "current": data.current_page,
        "principal": principal
    })


@router.get("/fragments/add-row")
def add_row_fragment(request: Request,
                     principal=Depends(with_auth(admin_only=True))):
    return templates.TemplateResponse("dashboard/plant/fragments/add_plant.html", {
        "request": request,
        "principal": principal
    })


@router.get("/fragments/edit-row/{plant_id}")
def edit_row_fragment(plant_id: int,
                      request: Request,
                      plant_service: PlantService = Depends(get_plant_service),
                      principal=Depends(with_auth(admin_only=True))):
    plant = plant_service.get_by_id(plant_id)
    return templates.TemplateResponse("dashboard/plant/fragments/edit_plant.html", {
        "request": request,
        "principal": principal,
        "plant": plant
    })


@router.get("/fragments/cancel-add-row")
def cancel_add_row_fragment():
    return {}


@router.get("/fragments/cancel-edit-row/{plant_id}")
def cancel_edit_row_fragment(plant_id: int,
                             request: Request,
                             plant_service: PlantService = Depends(get_plant_service),
                             principal=Depends(with_auth(admin_only=True))):
    plant = plant_service.get_by_id(plant_id)
    return templates.TemplateResponse("dashboard/plant/fragments/plant_row.html", {
        "request": request,
        "plant": plant,
        "principal": principal
    })


@router.post("/")
def create(entity: PlantCreate,
           request: Request,
           plant_service: PlantService = Depends(get_plant_service),
           principal=Depends(with_auth(admin_only=True))):
    plant = plant_service.create(entity)
    return templates.TemplateResponse("dashboard/plant/fragments/plant_row.html", {
        "request": request,
        "plant": plant,
        "principal": principal
    })


@router.put("/{plant_id}")
def replace(plant_id: int,
            request: Request,
            entity: PlantUpdate,
            plant_service: PlantService = Depends(get_plant_service),
            principal=Depends(with_auth(admin_only=True))):
    plant = plant_service.replacement_update(plant_id, entity)
    return templates.TemplateResponse("dashboard/plant/fragments/plant_row.html", {
        "request": request,
        "plant": plant,
        "principal": principal
    })


@router.delete("/{plant_id}")
def delete(plant_id: int,
           request: Request,
           plant_service: PlantService = Depends(get_plant_service),
           principal=Depends(with_auth(admin_only=True))):
    _ = plant_service.delete(plant_id)
    return templates.TemplateResponse("components/ui/alert.html", {
        "request": request,
        "msg": f"Plant {plant_id} has been deleted",
        "cls": ALERT_TYPE["success"],
        "principal": principal
    })
