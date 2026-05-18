from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import Base
from enum import Enum
from sqlalchemy import Enum as SQLEnum



class RuoloUtente(Enum):
    mixerista = "mixerista"
    utente = "utente"
    amministratore = "amministratore"
    video = "video"

class User(Base):
    __tablename__ = 'user'
    username = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(SQLEnum(RuoloUtente), nullable=False)

    scene_participation = relationship("SceneParticipation", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    layouts = relationship(
        "LayoutChannel",
        back_populates="user",
        primaryjoin="User.username == LayoutChannel.user_username",
        cascade="all, delete-orphan"
    )