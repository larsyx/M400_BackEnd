from enum import Enum
from sqlalchemy import Column, Enum as SQLEnum, Integer, String
from sqlalchemy.orm import relationship


from .base import Base

class TypeChannel(Enum):
    instrument = "instrument"
    drum = "drum"
    voice = "voice"

class Channel(Base):
    __tablename__ = 'channel'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    midi_address = Column(String, nullable=False, unique=True)
    type_channel = Column(SQLEnum(TypeChannel), nullable=True)

    layout_channel = relationship("LayoutChannel", back_populates="channel")