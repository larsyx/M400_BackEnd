from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from .base import Base

class Scene(Base):
    __tablename__ = 'scene'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    scene_participation = relationship("SceneParticipation", back_populates="scene", cascade="all, delete-orphan", passive_deletes=True)
    layouts = relationship(
        "LayoutChannel",
        back_populates="scene",
        primaryjoin="Scene.id == LayoutChannel.scene_id",
        cascade="all, delete-orphan"
    )