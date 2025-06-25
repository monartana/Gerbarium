from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Optional

from comment.model import Comment
from database import get_db
from favorite.model import Favorite
from util.filtering import search_and_sort

from plant.model import Plant
from plant.schema import PlantCreate, PlantUpdate


class PlantRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, plant_id: int):
        return (
            self.session.query(Plant)
            .filter(Plant.id == plant_id)
            .outerjoin(Comment, Plant.id == Comment.plant_id)
            .order_by(Comment.created_at)
            .first()
        )

    def fetch(
        self,
        page_size: int,
        page: int,
        search_query: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None
    ):
        return search_and_sort(
            self.session,
            Plant,
            search_query,
            sort_by,
            page,
            page_size,
            sort_direction
        )

    def create(self, entity: PlantCreate):
        db_plant = Plant(**entity.model_dump())

        self.session.add(db_plant)
        self.session.commit()
        self.session.refresh(db_plant)

        return db_plant

    def update(
        self,
        plant_id: int,
        plant_update: PlantUpdate
    ):
        db_plant = self.get_by_id(plant_id)
        if not db_plant:
            return None

        for var, value in vars(plant_update).items():
            setattr(db_plant, var, value)

        self.session.commit()
        self.session.refresh(db_plant)

        return db_plant

    def delete(self, item_id: int):
        db_plant = self.get_by_id(item_id)

        if not db_plant:
            return None

        db_favorites = self.session.query(Favorite).filter(Favorite.plant_id == item_id)
        if db_favorites is not None:
            for db_favorite in db_favorites:
                self.session.delete(db_favorite)

        self.session.delete(db_plant)
        self.session.commit()

        return db_plant


def get_plant_repository(db: Session = Depends(get_db)):
    return PlantRepository(db)
