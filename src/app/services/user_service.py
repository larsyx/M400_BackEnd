
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from app.dao.channel_dao import ChannelDAO
from app.dao.layout_canale_dao import LayoutCanaleDAO
from app.dao.partecipazione_scena_dao import PartecipazioneScenaDAO
from app.dao.user_dao import UserDAO
from app.dao.profile_dao import ProfileDAO
from app.dao.profile_layout_dao import ProfileLayoutDAO
from app.dao.aux_dao import AuxDAO
from fastapi.responses import RedirectResponse
import os
import json

from midi.midi_controller import MidiController, MidiListener, call_type

class UserService:
    def __init__(self):
        load_dotenv()
        self.userDAO = UserDAO()
        self.auxDAO = AuxDAO()
        self.partecipazioneScenaDAO = PartecipazioneScenaDAO()
        self.layoutCanaleDAO = LayoutCanaleDAO()
        self.channelDAO = ChannelDAO()
        self.profileDAO = ProfileDAO()
        self.profileLayoutDAO = ProfileLayoutDAO()
        self.templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "view", "user"))
        self.midiController = MidiController()
        self.postMainFader = [int(val,16) for val in os.getenv("Main_Post_Fix_Fader").split(",")]
        self.postName = [int(val,16) for val in os.getenv("Fader_Post_Name").split(",")]

    def load_scene(self, scenaID, userID, request):
        
        canali = self.layoutCanaleDAO.get_layout_channel(userID, scenaID)
        aux = self.partecipazioneScenaDAO.get_aux_user(userID, scenaID)
        hasBatteria = False

        if not aux:
            return RedirectResponse(url="/user/getScenes", status_code=303)

        for canale in canali:
            if not hasBatteria and canale.is_drum:
                hasBatteria = True
                break

        profiles = self.get_profiles(userID, scenaID)

        # auxs name
        listenAddressAuxName = []
        auxs = self.auxDAO.get_all_aux()
        for a in auxs:
            auxAddress = [int(x,16) for x in a.midi_address_main.split(",")]
            listenAddressAuxName.append(auxAddress + self.postName)

        resultsValueAuxName = MidiListener.init_and_listen(listenAddressAuxName, call_type.NAME) 
        resultsValueAuxSetName = {}

        for a in auxs:
            auxAddress = [int(x,16) for x in a.midi_address_main.split(",")]
            try:
                resultsValueAuxSetName[a.id] = resultsValueAuxName[tuple(auxAddress + self.postName)]
            except KeyError as k:
                print("errore chiave ", k)
                resultsValueAuxSetName[a.id] = ""


        return self.templates.TemplateResponse("scene.html", {"request": request, "canali": canali, "aux" : aux, "auxs" : auxs, "auxNames" : resultsValueAuxSetName, "hasBatteria" : hasBatteria, 'profiles' : profiles})

    def set_layout(self, userID, scenaID, request):  
        channels = self.channelDAO.get_all_channels()
        layouts = self.layoutCanaleDAO.get_layout_channel(userID, scenaID)
        

        layout_canali_ids = {layout_canale.channel_id for layout_canale in layouts}
        channel = [channel for channel in channels if channel.id not in layout_canali_ids]

        return self.templates.TemplateResponse("layout.html", {"request": request, "canali": channel, "layout": layouts})
      
    def set_fader(self, token, canaleId, value, indirizzoAux):
        canaleAddress = self.channelDAO.get_channel_address(canaleId)
    
        if(canaleAddress != None):
            addressAuxhex = [int(x,16) for x in indirizzoAux.split(",")]
            channelAddresshex = [int(x,16) for x in canaleAddress.split(",")]

            indirizzo = channelAddresshex + addressAuxhex
            
            self.midiController.send_command(indirizzo, MidiController.convert_fader_to_hex(int(value)), token)
        
    def set_fader_main(self, token, value, auxAddress):
        addressAuxhex = [int(x,16) for x in auxAddress.split(",")] + self.postMainFader
        self.midiController.send_command(addressAuxhex, MidiController.convert_fader_to_hex(int(value)), token)

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
            return "Errore parametri"

        return self.profileDAO.get_all_profile_user(user, scene_id)

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
    