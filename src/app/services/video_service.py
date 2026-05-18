from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.dao.channel_dao import ChannelDAO
from app.dao.aux_dao import AuxDAO
from app.dao.user_dao import UserDAO
from midi.midi_controller import MidiController, MidiListener, call_type
import os 
import json

class VideoService():

    def __init__(self):
        load_dotenv()
        self.userDAO = UserDAO()
        self.channelDAO = ChannelDAO()
        self.auxDAO = AuxDAO()
        self.postMainFader = [int(val,16) for val in os.getenv("Main_Post_Fix_Fader").split(",")]
        self.postMainSwitch = [int(val,16) for val in os.getenv("Main_Post_Fix_Switch").split(",")]
        self.postName = [int(val,16) for val in os.getenv("Fader_Post_Name").split(",")]
        self.postLink = [int(val,16) for val in os.getenv("Fader_Post_link").split(",")]
        self.auxId = os.getenv("VIDEO_AUX_ID") 
        self.templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "view", "video"))
        self.midiController = MidiController()

    def load_scene(self, request):
        
        channels = self.channelDAO.get_all_channels()
        listenAddressName = []
        listenAddressLink = []

        for channel in channels:
            channelAddress = [int(x,16) for x in channel.midi_address.split(",")] 
            
            listenAddressName.append(channelAddress + self.postName)
            listenAddressLink.append(channelAddress + self.postLink)

        # get names
        resultsValueName = MidiListener.init_and_listen(listenAddressName, call_type.NAME)       
        resultsValueSetName = []

        for channel in channels:
            channelAddress = [int(x,16) for x in channel.midi_address.split(",")] 
            try:
                resultsValueSetName.append(resultsValueName[tuple(channelAddress + self.postName)])
            except KeyError as k:
                print("errore chiave ch name:", k)
                resultsValueSetName.append(0)

        # get linked channels
        resultsValueLink = MidiListener.init_and_listen(listenAddressLink, call_type.SWITCH)    
        resultsValueSetLink = []

        for address in listenAddressLink:
            try:
                resultsValueSetLink.append(not resultsValueLink[tuple(address)])
            except KeyError as k:
                print("errore chiave ch link:", k)
                resultsValueSetLink.append(False)

        # only the second link
        skip = False
        for i in range(len(resultsValueSetLink)-1):
            if not skip:
                if resultsValueSetLink[i]:
                    if resultsValueSetLink[i+1]:
                        resultsValueSetLink[i] = False
                        skip = True
                    if not resultsValueSetLink[i+1]:
                        resultsValueSetLink[i] = False
                        resultsValueSetLink[i+1] = True
                        skip = True
            else:
                skip = False

        couple = list(zip(channels, resultsValueSetName, resultsValueSetLink))        
    

        return self.templates.TemplateResponse("scene.html", {"request": request, "canali": couple})

    def set_fader(self, token, channel_id, value):
        channel_address = self.channelDAO.get_channel_address(channel_id)
    
        if(channel_address != None):
            aux = self.auxDAO.get_aux_by_id(self.auxId) 

            channelAddresshex = [int(x,16) for x in channel_address.split(",")]
            address_aux = [int(x,16) for x in aux.midi_address.split(",")]

            address = channelAddresshex + address_aux
            
            self.midiController.send_command(address, MidiController.convert_fader_to_hex(int(value)), token)

    def set_fader_main(self, token, value):
        aux = self.auxDAO.get_aux_by_id(self.auxId) 

        if aux:
            address_aux_main = [int(x,16) for x in aux.midi_address_main.split(",")] + self.postMainFader
            self.midiController.send_command(address_aux_main, MidiController.convert_fader_to_hex(int(value)), token)

    def set_switch_main(self, token, value):
        aux = self.auxDAO.get_aux_by_id(self.auxId)

        if aux:
            address_aux_main = [int(x,16) for x in aux.midi_address_main.split(",")] + self.postMainSwitch
            self.midiController.send_command(address_aux_main, MidiController.convert_switch_to_hex(value), token)

    def get_faders_value(self):

        channels = self.channelDAO.get_all_channels()
        aux = self.auxDAO.get_aux_by_id(self.auxId)

        listen_address_fader = []

        # initialize the list of addresses for request and listen
        aux_address = [int(x,16) for x in aux.midi_address.split(",")] 
        aux_address_main = [int(x,16) for x in aux.midi_address_main.split(",")] + self.postMainFader
        aux_address_main_switch = [int(x,16) for x in aux.midi_address_main.split(",")] + self.postMainSwitch

        for channel in channels:
            channel_address = [int(x,16) for x in channel.midi_address.split(",")]
            listen_address_fader.append(channel_address + aux_address)


        listen_address_fader.append(aux_address_main)

        # channel request and listen
        results_value = MidiListener.init_and_listen(listen_address_fader, call_type.CHANNEL)
        results_value_set = {}
        
        # get channel value
        for channel in channels:
            channel_midi = self.channelDAO.get_channel_address(channel_id = channel.id)
            channel_address = [int(x,16) for x in channel_midi.split(",")] + aux_address
            try:
                results_value_set[channel.id] = results_value[tuple(channel_address)]
            except KeyError as e:
                print(f"error key {e}")
                results_value_set[channel.id] = 0

        try:
            results_value_set["main"] = results_value[tuple(aux_address_main)]
        except KeyError as e:
            print(f"error key {e}")
            results_value_set["main"] = 0

        # switch Main request and listen
        results_value_switch = MidiListener.init_and_listen([aux_address_main_switch], call_type.SWITCH)

        try:
            results_value_set["switch"] = results_value_switch[tuple(aux_address_main_switch)]
        except KeyError as e:
            print(f"error key {e}")
            results_value_set["switch"] = False

        return json.dumps(results_value_set, indent=2)
