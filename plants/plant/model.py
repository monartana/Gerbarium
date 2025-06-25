from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base
from .schema import WaterNeeds, LightNeeds, TemperaturePreference, HumidityNeeds, Location

class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, index=True)
    species = Column(String, index=True)
    description = Column(String)
    image_url = Column(String)
    water_needs = Column(SQLEnum(WaterNeeds), default=WaterNeeds.MODERATE)
    light_needs = Column(SQLEnum(LightNeeds), default=LightNeeds.MODERATE)
    temperature_preference = Column(SQLEnum(TemperaturePreference), default=TemperaturePreference.MODERATE)
    humidity_needs = Column(SQLEnum(HumidityNeeds), default=HumidityNeeds.MODERATE)
    location = Column(SQLEnum(Location), default=Location.BOTH)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
