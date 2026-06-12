from sqlalchemy import Column, Enum as SQLEnum, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from enum import Enum


from .base import Base


class TypeChannel(Enum):
    instrument = "instrument"
    drum = "drum"
    voice = "voice"


class LayoutChannel(Base):
    __tablename__ = 'layout_channel'

    channel_id = Column(Integer, ForeignKey('channel.id'), primary_key=True)
    scene_id = Column(Integer, ForeignKey('scene.id', ondelete="CASCADE"), primary_key=True)
    user_username = Column(String, ForeignKey('user.username', ondelete="CASCADE"), primary_key=True)

    position = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    type_channel = Column(SQLEnum(TypeChannel), nullable=True)
    

    channel = relationship("Channel", back_populates="layout_channel")

    scene = relationship("Scene", back_populates="layouts") 
    user = relationship("User", back_populates="layouts")   