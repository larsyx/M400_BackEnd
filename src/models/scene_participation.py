from sqlalchemy import Column, String, Integer, ForeignKey, and_
from sqlalchemy.orm import relationship, foreign, remote


from .base import Base

class SceneParticipation(Base):
    __tablename__ = 'scene_participation'

    scene_id = Column(Integer, ForeignKey('scene.id', ondelete="CASCADE"), primary_key=True)
    user_username = Column(String, ForeignKey('user.username', ondelete="CASCADE"), primary_key=True)
    aux_id = Column(Integer, ForeignKey('aux.id'), nullable=False)

    scene = relationship("Scene", back_populates="scene_participation", passive_deletes=True)
    user = relationship("User", back_populates="scene_participation", passive_deletes=True)
    aux = relationship("Aux", back_populates="scene_participation")

    profiles = relationship("Profile", back_populates="scene_participation", cascade="all, delete-orphan")
