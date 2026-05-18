from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, foreign


from .base import Base


class Channel(Base):
    __tablename__ = 'channel'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable = True)
    midi_address = Column(String, nullable=False, unique=True)

    layout_channel = relationship("LayoutChannel", back_populates="channel")