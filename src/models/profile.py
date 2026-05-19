from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, ForeignKeyConstraint
from sqlalchemy.orm import relationship


from .base import Base

class Profile(Base):

    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    scene_id = Column(Integer, nullable=False)
    user_username = Column(String,  nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ['scene_id', 'user_username'], 
            ['scene_participation.scene_id', 'scene_participation.user_username'], 
            ondelete="CASCADE" 
        ),
    )


    scene_participation = relationship(
        "SceneParticipation",
        back_populates="profiles"
    )

    profile_layout = relationship("ProfileLayout", back_populates="profile", passive_deletes=True)