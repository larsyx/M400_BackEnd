from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from .base import Base

class Aux(Base):
    __tablename__ = 'aux'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    midi_address = Column(String, nullable=False, unique=True)
    midi_address_main = Column(String, nullable=False, unique=True)

    scene_participation = relationship("SceneParticipation", back_populates="aux")
