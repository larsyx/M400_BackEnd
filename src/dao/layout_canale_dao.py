from sqlalchemy import desc
from Database.database import DBSession
from models.channel import Channel
from models.layout_channel import LayoutChannel, TypeChannel
from dao.channel_dao import ChannelDAO 
import json
import os


class LayoutCanaleDAO:

    def __init__(self):
        self.db = DBSession.get()
        
    def get_layout_channel_by_id(self, user, scene, canale):
        try:
            layout = self.db.query(LayoutChannel).filter(
                LayoutChannel.user_username == user,
                LayoutChannel.scene_id == scene,
                LayoutChannel.channel_id == canale
            ).first()
            return layout
        except Exception as e:
            print(f"Error retrieving layout id: {e}")
            return None
        
    def get_layout_channel(self, user, scene):
        try:
            layout = self.db.query(LayoutChannel).filter(
                LayoutChannel.user_username == user,
                LayoutChannel.scene_id == scene
            ).order_by(LayoutChannel.position).all()
            return layout
        except Exception as e:
            print(f"Error retrieving layout: {e}")
            return None
        
    def get_default_layout_channel(self):
        try:
            layout = self.db.query(LayoutChannel).filter(
                LayoutChannel.user_username == 'admin',
                LayoutChannel.scene_id == -1
            ).order_by(LayoutChannel.position).all()
            return layout
        except Exception as e:
            print(f"Error retrieving layout: {e}")
            return None
      
    def remove_layout_channel(self, user, scene):
        try:
            layouts = self.db.query(LayoutChannel).filter(
                LayoutChannel.user_username == user,
                LayoutChannel.scene_id == scene
            )

            for layout in layouts:
                self.db.delete(layout)
        except Exception as e:
            print(f"Error remove layout: {e}")
            return None
           
    def set_layout_channel(self, user, scene, canale, posizione, descrizione, type_channel):
        try:
            layout = self.get_layout_channel_by_id(user, scene, canale)

            if not layout:
                layout = LayoutChannel(
                    scene_id=scene,
                    channel_id=canale,
                    user_username=user,
                )
            
            layout.description = descrizione
            layout.position = posizione
            layout.type_channel = type_channel

            self.db.add(layout)
            self.db.commit()

            return layout
        except Exception as e:
            print(f"Error setting layout: {e}")
            return None
        