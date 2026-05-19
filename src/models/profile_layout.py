
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, ForeignKeyConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base

class ProfileLayout(Base):
    __tablename__ = "profile_layout"


    #layout
    channel_id = Column(Integer, primary_key=True)
    scene_id = Column(Integer, primary_key=True)
    user_username = Column(String,primary_key=True)

    #profile
    profile_id = Column(Integer, ForeignKey('profile.id', ondelete="CASCADE"), primary_key=True)
    
    value = Column(Integer, nullable=False)
    

    __table_args__ = (
        ForeignKeyConstraint(
            ['channel_id', 'scene_id', 'user_username'], 
            ['layout_channel.channel_id','layout_channel.scene_id', 'layout_channel.user_username'], 
            ondelete="CASCADE" 
        ),
        CheckConstraint('value >= 0 AND value <= 100', name='value_range'),
    )

    profile = relationship('Profile', back_populates='profile_layout', passive_deletes=True)