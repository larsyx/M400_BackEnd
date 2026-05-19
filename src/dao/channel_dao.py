from Database.database import DBSession
from models.channel import Channel


class ChannelDAO:
    def __init__(self):
        self.db = DBSession.get()

    def get_all_channels(self):
         try:
            channels = self.db.query(Channel).all()
            return channels
         except Exception as e:
            print(f"Error retrieving all channels: {e}")
            return None

    def get_channel_by_id(self, channel_id):
        try:
            channel = self.db.query(Channel).filter(Channel.id == channel_id).first()
            
            return channel
        except Exception as e:
            self.db.rollback()
            print(f"Error retrieving channels: {e}")
            return None

    def get_channel_address(self, channel_id):
        channel = self.get_channel_by_id(channel_id)

        return channel.midi_address if channel else None
    
    def get_channel_by_address(self, address):
        channel = self.db.query(Channel).filter(Channel.midi_address == address)[0]
        if channel:
            return channel
        else:
            return None
        
    def update_channel_description(self, id, value):
        try:
            self.db.query(Channel).filter(Channel.id == id).update({Channel.description: value})
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error updating channel: {e}")
            return False
