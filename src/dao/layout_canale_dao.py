from sqlalchemy import desc
from Database.database import DBSession
from models.channel import Channel
from models.layout_channel import LayoutChannel
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
           
    def set_layout_channel(self, user, scene, canale, posizione, descrizione, type_channel):
        try:
            layout = self.get_layout_channel_by_id(user, scene, canale)
            layout.description = descrizione
            layout.position = posizione
            layout.type_channel = type_channel

            self.db.add(layout)
            self.db.commit()

            return layout
        except Exception as e:
            print(f"Error setting layout: {e}")
            return None
        
    def add_layout_channel(self, user, scene, canale, descrizione):
        try: 
            layout = self.db.query(LayoutChannel).filter(
                LayoutChannel.user_username == user,
                LayoutChannel.scene_id == scene
            ).order_by(desc(LayoutChannel.position)).first()
            posizione=0
            if(layout):
                posizione = layout.position +1

            layout = LayoutChannel(
                scene_id=scene,
                channel_id=canale,
                user_username=user,
                position=posizione,
                description=descrizione
            )

            self.db.add(layout)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error adding layout: {e}")
            return None
        
    def remove_layout_channel(self, user, scene, canale):
        try:
            channelToRemove = self.get_layout_channel_by_id(user, scene, canale)

            updateChannel = self.db.query(LayoutChannel).filter(
                    LayoutChannel.user_username == user,
                    LayoutChannel.scene_id == scene,
                    LayoutChannel.position > channelToRemove.position
            ).all()

            for channel in updateChannel:
                self.set_layout_channel(user,scene,channel.channel_id, channel.position-1, channel.description)

            self.db.delete(channelToRemove)
            self.db.commit()
            return True
        
        except Exception as e:
            print(f"Error removing layout: {e}")
            return None

    def add_default_layout_channel(self, user, scene):
        file_path = os.path.join(os.path.dirname(__file__), "..", "Database", "default_layout.json")
        with open(file_path, "r") as json_data:
            data = json.load(json_data)


            channels = [ch for ch in data.get('channels', [])]
            channels_ids = [ch['id'] for ch in channels]
            drums = [d for d in data.get('drums', []) if d['id'] not in channels_ids]

            if self.get_layout_channel(user, scene) is not None and len(self.get_layout_channel(user, scene)) > 0:
                return True
            
            channelDAO = ChannelDAO()

            for channel in channels:
                channel_obj = channelDAO.get_channel_by_id(channel['id'])
                if channel_obj is not None:
                    self.add_layout_channel(user, scene, channel['id'], channel['descrizione'], False)


            for drum in drums:
                channel_obj = channelDAO.get_channel_by_id(drum['id'])
                if channel_obj is not None:
                    self.add_layout_channel(user, scene, drum['id'], drum['descrizione'], True)

