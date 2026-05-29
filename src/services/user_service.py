
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
        self.midi_controller = MidiController()
        self.aux_service = AuxService()

    def load_scene(self, scene_id, user_id):
        channel = self.layout_channel_dao.get_layout_channel(user_id, scene_id)
        aux = self.scene_partecipation_dao.get_aux_user(user_id, scene_id)

        profiles = self.get_profiles(user_id, scene_id)

        aux = self.aux_service.load_aux_names()
        fader = self.aux_service.load_fader_aux_scene(aux[0].id, channel)

        return UserHomeDTO(fader=fader, aux=aux, profile=profiles)

    def set_layout(self, userID, scenaID, request):  
        channels = self.channel_dao.get_all_channels()
        layouts = self.layout_channel_dao.get_layout_channel(userID, scenaID)
        

        layout_canali_ids = {layout_canale.channel_id for layout_canale in layouts}
        channel = [channel for channel in channels if channel.id not in layout_canali_ids]

        return self.templates.TemplateResponse("layout.html", {"request": request, "canali": channel, "layout": layouts})
      
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
    def create_profile(self, name, user, scene_id, profiles):
        if name == None or name == "" or scene_id == None or user == None or user == "":
            return "Errore parametri"

        profile = self.profileDAO.create_profile(name, scene_id, user)
        if profile and profiles != None and len(profiles) > 0:
            self.profileLayoutDAO.update_profiles_layout(profile.id, user, scene_id, profiles)

        return json.dumps({"id" : profile.id, "name" : profile.name})


    def delete_profile(self, id, user, scene_id):
        if id == None or  user == None or user == "":
            return "Errore parametri"
            
        return self.profileDAO.delete_profile(id, user, scene_id)

    def delete_profiles(self, user, scene_id):
        if id == None or  user == None or user == "":
            return "Errore parametri"
            
        profiles = self.profileDAO.get_all_profile_user(user, scene_id)

        for profile in profiles:
            self.delete_profile(profile.id, user, scene_id)

        return True


    def update_profile(self, profile_id, user, scene_id, profiles):
        if id == None or user == None or user == "":
            return "Errore parametri"

        if profiles != None and len(profiles) > 0:
            self.profileLayoutDAO.update_profiles_layout(profile_id, user, scene_id, profiles)

    def get_profiles(self, user, scene_id):
        if scene_id == None or user == None or user == "":
            raise Exception("Missing parameters")

        return self.profile_dao.get_all_profile_user(user, scene_id)

    def load_profile(self, user, token, scene_id, profile_id):
        profiles =  self.profileLayoutDAO.get_profile_layout_user_scene(user, profile_id, scene_id)

        aux = self.partecipazioneScenaDAO.get_aux_user(user, scene_id)

        response = {}

        if aux:
            for profile in profiles:
                response[profile.channel_id] = profile.value
                self.set_fader(token, profile.channel_id, profile.value, aux.midi_address)

        return json.dumps(response)

    def get_aux(self, aux_id):
        return self.auxDAO.get_aux_by_id(aux_id)
    