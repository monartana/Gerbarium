from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer,
                primary_key=True,
                autoincrement=True,
                index=True)
    text = Column(String,
                  nullable=False)

    plant_id = Column(Integer,
                      ForeignKey("plants.id"))
    user_id = Column(Integer,
                     ForeignKey("users.id"))
    plant = relationship("Plant",
                         backref="comments",
                         cascade="delete")
    user = relationship("User",
                        backref="comments",
                        cascade="delete")

    created_at = Column(DateTime(timezone=True),
                        default=func.now())
    updated_at = Column(DateTime(timezone=True),
                        default=func.now(),
                        onupdate=func.now())
