from fastapi import Depends

from favorite.repository import FavoriteRepository, get_favorite_repository
from favorite.schema import FavoriteCreate, FavoriteRead, FavoritePage
from util.decorators import with_error_logger


class FavoriteService:
    def __init__(self, repo: FavoriteRepository) -> None:
        self.favorite_repository = repo

    @with_error_logger
    def fetch_by_user_id(self, user_id: int,
                         page_size: int, page: int):
        db_page = self.favorite_repository.fetch_by_user_id(user_id, page_size, page)
        return FavoritePage.from_orm(db_page)

    @with_error_logger
    def toggle(self, entity: FavoriteCreate):
        db_favorite = self.favorite_repository.fetch_by_user_and_plant_id(entity.user_id, entity.plant_id)

        if db_favorite:
            db_favorite = self.favorite_repository.delete(db_favorite.id)
            return {"id": db_favorite.id}
        else:
            return FavoriteRead.from_orm(self.favorite_repository.create(entity))


def get_favorite_service(repo: FavoriteRepository = Depends(get_favorite_repository)):
    return FavoriteService(repo)
