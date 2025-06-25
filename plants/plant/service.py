from http import HTTPStatus
from typing import List, Optional
from fastapi import Depends, HTTPException

from plant.repository import PlantRepository, get_plant_repository
from plant.schema import PlantCreate, PlantUpdate, PlantRead, PlantPage, PlantReadWithComments
from util.decorators import with_error_logger
from database import get_db
from .recommendation import PlantRecommendationService, get_recommendation_service


class PlantService:
    def __init__(self,
                 repository: PlantRepository = Depends(get_plant_repository),
                 recommendation_service: PlantRecommendationService = Depends(get_recommendation_service)):
        self.repository = repository
        self.recommendation_service = recommendation_service

    @with_error_logger
    def get_by_id(self, plant_id: int):
        db_plant = self.repository.get_by_id(plant_id)

        if db_plant is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail=f"Plant with id: {plant_id} not found")

        return PlantReadWithComments.from_orm(db_plant)

    @with_error_logger
    def fetch(self,
              page_size: int,
              page: int,
              search_query: Optional[str] = None,
              sort_by: Optional[str] = None,
              sort_direction: Optional[str] = None):
        db_page = self.repository.fetch(
            page_size, page, search_query, sort_by, sort_direction)
        return PlantPage.from_orm(db_page)

    @with_error_logger
    def create(self, entity: PlantCreate):
        db_plant = self.repository.create(entity)
        return PlantRead.from_orm(db_plant)

    @with_error_logger
    def replacement_update(self,
                           plant_id: int,
                           plant_update: PlantUpdate):
        db_plant = self.repository.update(plant_id, plant_update)

        if db_plant is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail=f"Plant with id: {plant_id} not found")

        return PlantRead.from_orm(db_plant)

    @with_error_logger
    def patch_update(self,
                     plant_id: int,
                     plant_update: PlantUpdate):
        db_plant = self.repository.get_by_id(plant_id)

        if db_plant is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail=f"Plant with id: {plant_id} not found")

        for field, value in plant_update.dict(exclude_unset=True).items():
            setattr(db_plant, field, value)

        db_plant = self.repository.update(plant_id, db_plant)

        return PlantRead.from_orm(db_plant)

    @with_error_logger
    def delete(self, item_id: int):
        db_plant = self.repository.delete(item_id)
        return PlantRead.from_orm(db_plant)

    def get_similar_plants(self, plant_id: int, limit: int = 5) -> List[PlantRead]:
        """Get similar plants based on plant attributes."""
        return self.recommendation_service.get_similar_plants(plant_id, limit)

    def get_personalized_recommendations(self, user_id: int, limit: int = 5) -> List[PlantRead]:
        """Get personalized plant recommendations for a user."""
        return self.recommendation_service.get_personalized_recommendations(user_id, limit)


def get_plant_service(repository: PlantRepository = Depends(get_plant_repository),
                     recommendation_service: PlantRecommendationService = Depends(get_recommendation_service)) -> PlantService:
    return PlantService(repository, recommendation_service)
