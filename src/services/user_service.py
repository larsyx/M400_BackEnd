
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from dao.channel_dao import ChannelDAO
from dao.layout_canale_dao import LayoutCanaleDAO
from dao.partecipazione_scena_dao import PartecipazioneScenaDAO
from dao.user_dao import UserDAO
from dao.profile_dao import ProfileDAO
from dao.profile_layout_dao import ProfileLayoutDAO
from dao.aux_dao import AuxDAO
from fastapi.responses import RedirectResponse
from dto.response.channel_layout_dto import ChannelLayoutDTO
from dto.response.fader_dto import FaderDTO
from dto.response.profile_dto import ProfileDTO
from dto.response.user_home_dto import UserHomeDTO
from services.aux_service import AuxService
from settings import POST_MAIN_FADER, POST_NAME
import os
import json

from midi.midi_controller import MidiController, MidiListener, call_type
from utils.utils import string_to_hex_list

class UserService:
    def __init__(self):
        self.user_dao = UserDAO()
        self.aux_dao = AuxDAO()
        self.scene_partecipation_dao = PartecipazioneScenaDAO()
        self.layout_channel_dao = LayoutCanaleDAO()
        self.channel_dao = ChannelDAO()
        self.profile_dao = ProfileDAO()
        self.profile_layout_dao = ProfileLayoutDAO()
        self._midi_controller = None
        self.aux_service = AuxService()

    @property
    def midi_controller(self):
        if self._midi_controller is None:
            self._midi_controller = MidiController()
        return self._midi_controller
    
    
    def load_scene(self, scene_id, user_id):
        try:
            channel = self.layout_channel_dao.get_layout_channel(user_id, scene_id)
            print([f"ch {ch.channel_id}" for ch in channel])
            aux_user = self.scene_partecipation_dao.get_aux_user(user_id, scene_id)

            profiles = self.profile_dao.get_all_profile_user(user_id, scene_id)

            aux = self.aux_service.load_aux_names()
            fader = self.aux_service.load_fader_aux_scene(aux_user.id, channel)
            return UserHomeDTO(fader=fader, aux=aux, profile=profiles, auxUser=aux_user)
        except Exception as e:
            print(f"Error load scene: {e}")
            return None

    #layout
    def get_channel_layout(self, user_id, scene_id):
        layouts = self.layout_channel_dao.get_layout_channel(user_id, scene_id)
  
        channel_names = self.aux_service.load_fader_names(None)

        channel_map = {
            channel.id: ChannelLayoutDTO(
                channel_id=channel.id,
                name=channel.name,
                description=channel.description if channel.description else channel.name,
                type=None
            )
            for channel in channel_names
        }
        
        for layout in layouts:
            if layout.channel_id in channel_map:
                ch = channel_map[layout.channel_id]
                ch.position = layout.position
                ch.type = layout.type_channel
                ch.selected = True

        return list(channel_map.values())
        

    def set_default_layout(self, user_id, scene_id):
        self.layout_channel_dao.remove_layout_channel(user_id, scene_id)

        channels = self.channel_dao.get_all_channels()
        layouts = self.layout_channel_dao.get_default_layout_channel()
        
        self.layout_channel_dao.remove_layout_channel(user_id, scene_id)
        
        for layout in layouts:
            self.layout_channel_dao.set_layout_channel(user_id, scene_id, layout.channel_id, layout.position, layout.description, layout.type_channel)
       
  
        channel_map = {
            channel.id: ChannelLayoutDTO(
                channel_id=channel.id,
                name=channel.name,
                description=channel.description if channel.description else channel.name,
                type=None
            )
            for channel in channels
        }
        
        for layout in layouts:
            if layout.channel_id in channel_map:
                ch = channel_map[layout.channel_id]
                ch.position = layout.position
                ch.type = layout.type_channel
                ch.selected = True

        return list(channel_map.values())
    

    def set_channel_layout(self, user_id, scene_id, layouts):     
        self.layout_channel_dao.remove_layout_channel(user_id, scene_id)
        
        for layout in layouts:
            if layout.selected:
                self.layout_channel_dao.set_layout_channel(user_id, scene_id, layout.channel_id, layout.position, layout.description, layout.type)

        return True
      
    def get_faders_value(self, user_id, scene_id, aux, aux_main):
        channels = self.layoutCanaleDAO.get_layout_channel(user_id, scene_id)
        listen_address = []
        aux = [int(x,16) for x in aux.split(",")]
        aux_main = [int(x,16) for x in aux_main.split(",")] + self.postMainFader

        for channel in channels:
            channel_midi = self.channelDAO.get_channel_address(channel_id = channel.channel_id)
            channel_address = [int(x,16) for x in channel_midi.split(",")] 

            listen_address.append(channel_address + aux)

        listen_address.append(aux_main)

        results_value = MidiListener.init_and_listen(listen_address, call_type.CHANNEL)

        results_value_set = {}

        for channel in channels:
            channel_midi = self.channelDAO.get_channel_address(channel_id = channel.channel_id)
            channel_address = [int(x,16) for x in channel_midi.split(",")] + aux
            try:
                results_value_set[channel.channel_id] = results_value[tuple(channel_address)]
            except KeyError as e:
                print(f"error key {e}")
                results_value_set[channel.channel_id] = 0

        try:
            results_value_set["main"] = results_value[tuple(aux_main)]
        except KeyError as e:
            print(f"error key {e}")
            results_value_set["main"] = 0

        return json.dumps(results_value_set, indent=2)

    def get_faders_names(self, list_channels):
        listenAddressName = []
        for channel in list_channels:
            channel_midi = self.channelDAO.get_channel_address(channel_id = channel)
            channel_address = [int(x,16) for x in channel_midi.split(",")] 
            listenAddressName.append(channel_address + self.postName)

        # get names channel
        resultsValueName = MidiListener.init_and_listen(listenAddressName, call_type.NAME)       
        resultsValueSetName = dict()

        # get channel name
        for channel in list_channels:
            channel_midi = self.channelDAO.get_channel_address(channel_id = channel)
            channel_address = [int(x,16) for x in channel_midi.split(",")] 
            try:
                resultsValueSetName[channel] = resultsValueName[tuple(channel_address + self.postName)]
            except KeyError as k:
                print("errore chiave ch name:", k)
                resultsValueSetName[channel] = 0

        return resultsValueSetName

    # profile
    def create_profile(self, user, scene_id, profile, profiles):
        if profile.name == None or profile.name == "" or scene_id == None or user == None or user == "":
            return "Errore parametri"

        profile = self.profile_dao.create_profile(profile.name, scene_id, user)
        if profile and profiles != None and len(profiles) > 0:
            self.profile_layout_dao.update_profiles_layout(profile.id, user, scene_id, profiles)

        return ProfileDTO(id=profile.id, name=profile.name)


    def delete_profile(self, id, user, scene_id):
        if id == None or  user == None or user == "":
            return "Errore parametri"
            
        return self.profile_dao.delete_profile(id, user, scene_id)

    def delete_profiles(self, user, scene_id):
        if id == None or  user == None or user == "":
            return "Errore parametri"
            
        profiles = self.profile_dao.get_all_profile_user(user, scene_id)

        for profile in profiles:
            self.delete_profile(profile.id, user, scene_id)

        return True


    def update_profile(self, user, scene_id, profile, profiles):
        if id == None or user == None or user == "":
            return "Errore parametri"

        if profile:
            self.profile_dao.update_profile(user, scene_id, profile.id, profile.name)
        if profiles != None and len(profiles) > 0:
            self.profile_layout_dao.update_profiles_layout(profile.id, user, scene_id, profiles)

    def get_profiles(self, user, scene_id):
        if scene_id == None or user == None or user == "":
            raise Exception("Missing parameters")

        return self.profile_dao.get_all_profile_user(user, scene_id)

    def load_profile(self, user, token, scene_id, profile_id, aux_id):
        profiles = self.profile_layout_dao.get_profile_layout_user_scene(user, profile_id, scene_id)
        if aux_id == -1:
            aux = self.scene_partecipation_dao.get_aux_user(user, scene_id)
        else:
            aux = self.aux_dao.get_aux_by_id(aux_id)

        if not aux:
            return []

        channels_by_id = {ch.id: ch for ch in self.channel_dao.get_all_channels() or []}

        fader_dto_list = []
        for profile in profiles:
            channel = channels_by_id.get(profile.channel_id)
            if channel is None:
                continue

            self.aux_service.set_fader_value(token, aux.id,  profile.channel_id, profile.value)

            fader_dto_list.append(FaderDTO(
                id=channel.id,
                name=channel.name,
                description=channel.description if channel.description else channel.name,
                value=profile.value,
                switch=False,
                type=channel.type_channel,
                position=channel.position
            ))

        return fader_dto_list

    def get_aux(self, aux_id):
        return self.aux_dao.get_aux_by_id(aux_id)
    