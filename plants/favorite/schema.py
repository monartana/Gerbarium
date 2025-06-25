from typing import List

from pydantic import Field

from common.schema import OrmBase
from plant.schema import PlantRead
from user.schema import UserRead


class FavoriteBase(OrmBase):
    pass


class FavoriteRead(FavoriteBase):
    id: int
    user: UserRead
    plant: PlantRead


class FavoritePage(OrmBase):
    items: List[FavoriteRead]
    current_page: int
    total_pages: int


class FavoriteCreate(FavoriteBase):
    plant_id: int
    user_id: int
