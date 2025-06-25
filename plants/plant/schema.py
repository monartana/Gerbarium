from typing import List, Optional
from enum import Enum
from pydantic import BaseModel
from datetime import datetime

from comment.schema import CommentRead
from common.schema import TimestampMixin, OrmBase


class WaterNeeds(str, Enum):
    LOW = "low"  # Desert plants, succulents
    MODERATE = "moderate"  # Most indoor plants
    HIGH = "high"  # Tropical plants, ferns


class LightNeeds(str, Enum):
    LOW = "low"  # Shade-loving plants
    MODERATE = "moderate"  # Partial sun
    HIGH = "high"  # Full sun plants


class TemperaturePreference(str, Enum):
    COLD = "cold"  # Below 15°C
    MODERATE = "moderate"  # 15-25°C
    WARM = "warm"  # Above 25°C


class HumidityNeeds(str, Enum):
    LOW = "low"  # Desert plants, succulents
    MODERATE = "moderate"  # Most indoor plants
    HIGH = "high"  # Tropical plants


class Location(str, Enum):
    INDOOR = "indoor"  # Indoor only plants
    OUTDOOR = "outdoor"  # Outdoor only plants
    BOTH = "both"  # Can be grown both indoors and outdoors


class PlantBase(BaseModel):
    name: str
    species: str
    description: str
    image_url: str
    water_needs: WaterNeeds = WaterNeeds.MODERATE
    light_needs: LightNeeds = LightNeeds.MODERATE
    temperature_preference: TemperaturePreference = TemperaturePreference.MODERATE
    humidity_needs: HumidityNeeds = HumidityNeeds.MODERATE
    location: Location = Location.BOTH


class PlantRead(PlantBase, TimestampMixin):
    id: int


class PlantReadWithComments(PlantRead):
    comments: List[CommentRead]


class PlantPage(OrmBase):
    items: List[PlantRead]
    current_page: int
    total_pages: int
    comments: List[CommentRead] = []


class PlantCreate(PlantBase):
    pass


class PlantUpdate(PlantBase):
    name: Optional[str] = None
    species: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    water_needs: Optional[WaterNeeds] = None
    light_needs: Optional[LightNeeds] = None
    temperature_preference: Optional[TemperaturePreference] = None
    humidity_needs: Optional[HumidityNeeds] = None
    location: Optional[Location] = None


class Plant(PlantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
