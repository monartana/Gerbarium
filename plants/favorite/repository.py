from math import ceil

from fastapi import Depends
from sqlalchemy import and_
from sqlalchemy.orm import Session

from database import get_db
from util.filtering import paginate

from favorite.model import Favorite
from favorite.schema import FavoriteCreate


class FavoriteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def fetch_by_user_id(self, user_id: int,
                         page_size: int, page: int):
        query = self.session.query(Favorite).filter(Favorite.user_id == user_id)
        items, total_items = paginate(query, page=page, page_size=page_size)

        return {"items": items, "total_pages": ceil(total_items / page_size), "current_page": page}

    def fetch_by_user_and_plant_id(self, user_id: int, plant_id: int):
        return (self.session.query(Favorite)
                .filter(and_(Favorite.user_id == user_id, Favorite.plant_id == plant_id))
                .first())

    def create(self, entity: FavoriteCreate):
        db_favorite = Favorite(**entity.model_dump())

        self.session.add(db_favorite)
        self.session.commit()
        self.session.refresh(db_favorite)

        return db_favorite

    def delete(self, item_id: int):
        db_favorite = self.session.query(Favorite).filter(Favorite.id == item_id).first()

        if not db_favorite:
            return None

        self.session.delete(db_favorite)
        self.session.commit()

        return db_favorite


def get_favorite_repository(db: Session = Depends(get_db)):
    return FavoriteRepository(db)
