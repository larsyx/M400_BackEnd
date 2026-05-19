from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, ForeignKeyConstraint, and_
from sqlalchemy.orm import relationship, foreign, remote


from .base import Base


class LayoutChannel(Base):
    __tablename__ = 'layout_channel'

    channel_id = Column(Integer, ForeignKey('channel.id'), primary_key=True)
    scene_id = Column(Integer, ForeignKey('scene.id', ondelete="CASCADE"), primary_key=True)
    user_username = Column(String, ForeignKey('user.username', ondelete="CASCADE"), primary_key=True)

    position = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    is_drum = Column(Boolean, nullable=False, default = False)

    channel = relationship("Channel", back_populates="layout_channel")

    scene = relationship("Scene", back_populates="layouts") 
    user = relationship("User", back_populates="layouts")   

