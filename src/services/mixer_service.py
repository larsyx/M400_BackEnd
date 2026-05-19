import json
import os
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from dao.channel_dao import ChannelDAO
from dao.dca_dao import DCA_DAO
from dao.aux_dao import AuxDAO
from dto.response.aux_dto import AuxDTO
from dto.response.fader_dto import FaderDTO
from midi.midi_controller import MidiController, MidiListener, call_type, get_eq_address_value, get_eq_channel
from dotenv import load_dotenv
import json


class MixerService:
    def __init__(self):
        self.channelDAO = ChannelDAO()
        self.dcaDAO = DCA_DAO()
        self.auxDAO = AuxDAO()

        load_dotenv()
        self.postMainFader = [int(val,16) for val in os.getenv("Main_Post_Fix_Fader").split(",")]
        self.postSwitch = [int(val,16) for val in os.getenv("Main_Post_Fix_Switch").split(",")]
        self.preMain = [int(val,16) for val in os.getenv("Main_Pre_Fix").split(",")]
        self.postEqSwitch = [int(val,16) for val in os.getenv("EQ_Post_Switch").split(",")]
        self.postName = [int(val,16) for val in os.getenv("Fader_Post_Name").split(",")]
        self.postLink = [int(val,16) for val in os.getenv("Fader_Post_link").split(",")]
        self.pre_preamp = [int(val,16) for val in os.getenv("Preamp_Pre").split(",")]
        self.post_preamp = [int(val,16) for val in os.getenv("Preamp_Post").split(",")]
        self.dca_fader_post = [int(val,0) for val in os.getenv("Dca_Fader_Post").split(",")]
        self.dca_switch_post = [int(val,0) for val in os.getenv("Dca_Switch_Post").split(",")]
        self.templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "view", "mixer"))
        self.midiController = MidiController()

    def load_fader(self):
        channels = self.channelDAO.get_all_channels()

        order = self.load_disposition()

        # get value canali
        listen_address_fader = []
        listen_address_switch = []
        listen_address_name = []
        listen_address_link = []

        # initialize the list of addresses for request and listen
        for channel in channels:
            channel_address = [int(x,16) for x in channel.midi_address.split(",")] 
            
            listen_address_fader.append(channel_address + self.postMainFader)
            listen_address_switch.append(channel_address + self.postSwitch)
            listen_address_name.append(channel_address + self.postName)
            listen_address_link.append(channel_address + self.postLink)

        listen_address_fader.append(self.preMain + self.postMainFader)
        listen_address_switch.append(self.preMain + self.postSwitch)

        # channel request and listen
        results_value = MidiListener.init_and_listen(listen_address_fader, call_type.CHANNEL)
        results_value_switch = MidiListener.init_and_listen(listen_address_switch, call_type.SWITCH)     
        results_value_name = MidiListener.init_and_listen(listen_address_name, call_type.NAME)       
        results_value_link = MidiListener.init_and_listen(listen_address_link, call_type.SWITCH)    

        fader_dto_list = []

        for channel in channels:
            channel_address = [int(x,16) for x in channel.midi_address.split(",")] 
            value = results_value.get((tuple(channel_address + self.postMainFader)), 0)
            name = results_value_name.get((tuple(channel_address + self.postName)), channel.name)
            switch = results_value_switch.get((tuple(channel_address + self.postSwitch)), False)
            link = results_value_link.get((tuple(channel_address + self.postLink)), False)

            fader_dto_list.append(FaderDTO(id=channel.id, value=value, name=channel.name, description=name, switch=switch, link=link))

        value_main = results_value.get((tuple(self.preMain + self.postMainFader)), 0)
        switch_main = results_value_switch.get((tuple(self.preMain + self.postSwitch)), False)

        fader_dto_list.append(FaderDTO(id=0, value=value_main, name="Main", switch=switch_main))

        return fader_dto_list
    

    def load_dca(self):
        dcas = self.dcaDAO.get_dca()

        # get value canali
        listen_address_fader = []
        listen_address_switch = []
        listen_address_name = []

        # initialize the list of addresses for request and listen
        for dca in dcas:
            dca_address = [int(x,16) for x in dca.midi_address.split(",")] 
            
            listen_address_fader.append(dca_address + self.postMainFader)
            listen_address_switch.append(dca_address + self.postSwitch)
            listen_address_name.append(dca_address + self.postName)

                # channel request and listen
        results_value = MidiListener.init_and_listen(listen_address_fader, call_type.CHANNEL)
        results_value_switch = MidiListener.init_and_listen(listen_address_switch, call_type.SWITCH)     
        results_value_name = MidiListener.init_and_listen(listen_address_name, call_type.NAME)

        dca_dto_list = []

        for dca in dcas:
            dca_address = [int(x,16) for x in dca.midi_address.split(",")] 
            value = results_value.get((tuple(dca_address + self.postMainFader)), 0)
            name = results_value_name.get((tuple(dca_address + self.postName)), dca.name)
            switch = results_value_switch.get((tuple(dca_address + self.postSwitch)), False)

            dca_dto_list.append(FaderDTO(id=dca.id, value=value, name=dca.name, description=name, switch=switch))

        return dca_dto_list
    
    def load_aux_names(self):
        listen_address_aux_name = []
        auxs = self.auxDAO.get_all_aux()

        for aux in auxs:
            address = [int(x,16) for x in aux.midi_address_main.split(",")]
            listen_address_aux_name.append(address + self.postName)

        results_value_aux_name = MidiListener.init_and_listen(listen_address_aux_name, call_type.NAME) 
        aux_dto_list = []

        for aux in auxs:
            address = [int(x,16) for x in aux.midi_address_main.split(",")] 
            
            name = results_value_aux_name.get((tuple(address + self.postName)), aux.name)
            aux_dto_list.append(AuxDTO(id=aux.id, name=name))

        return aux_dto_list

    def load_scenes(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "Database", "scenes.json"), "r") as file:
            scene = json.load(file)

        return scene.get('scenes', [])

    def get_aux_parameters(self, aux_id):
        aux = self.auxDAO.get_aux_by_id(aux_id)
        channels = self.channelDAO.get_all_channels()
        if aux and channels:
            address_aux = [int(x, 16) for x in aux.midi_address.split(",")]

            aux_addresses_fader = []
            for channel in channels:
                channel_address = [int(x, 16) for x in channel.midi_address.split(",")]
                aux_addresses_fader.append(channel_address + address_aux)

            aux_address = [int(x,16) for x in aux.midi_address_main.split(",")] 
            aux_addresses_fader.append(aux_address + self.postMainFader)
            results_value = MidiListener.init_and_listen(aux_addresses_fader, call_type.CHANNEL)
           
            results_value_set = {}
            
            # get channel value
            for channel in channels:
                channel_address = [int(x,16) for x in channel.midi_address.split(",")] 
                try:
                    results_value_set[channel.id] = results_value[tuple(channel_address + address_aux)]
                except KeyError as k:
                    print("errore chiave ", k)
                    results_value_set[channel.id] = 0


            try:
                results_value_set["main"] = results_value[tuple(aux_address + self.postMainFader)]
            except KeyError as k:
                print("errore chiave ", k)
                results_value_set["main"] = 0

            result_switch_main = MidiListener.init_and_listen([[int(x,16) for x in aux.midi_address_main.split(",")] + self.postSwitch], call_type.SWITCH)

            response = {
                "channels" : results_value_set,
                "switch" : next(iter(result_switch_main.values()))
            }

            return json.dumps(response, indent=4)

        return None

    def set_fader_value(self, token, canaleId, value):

        canaleAddress = self.channelDAO.get_channel_address(canaleId)
        
        if(canaleAddress != None):
            channelAddresshex = [int(x,16) for x in canaleAddress.split(",")]

            indirizzo = channelAddresshex + self.postMainFader
            
            self.midiController.send_command(indirizzo, MidiController.convert_fader_to_hex(int(value)), token)

    def set_switch_channel(self, token, canaleId, switch):
        canaleAddress = self.channelDAO.get_channel_address(canaleId)
        
        if(canaleAddress != None):
            channelAddresshex = [int(x,16) for x in canaleAddress.split(",")]

            indirizzo = channelAddresshex + self.postSwitch
            self.midiController.send_command(indirizzo, MidiController.convert_switch_to_hex(switch), token)

    def set_main_fader_value(self, token, value):

        indirizzo = self.preMain + self.postMainFader
        
        self.midiController.send_command(indirizzo, MidiController.convert_fader_to_hex(int(value)), token)

    def set_main_switch_channel(self, token, switch):
    
        indirizzo = self.preMain + self.postSwitch
        self.midiController.send_command(indirizzo, MidiController.convert_switch_to_hex(switch), token)

    def set_dca_fader_value(self, token, dca_id, value):
        dca = self.dcaDAO.get_dca_by_id(dca_id)

        if dca:
            address = [int(x, 16) for x in dca.midi_address.split(",")] + self.dca_fader_post
            self.midiController.send_command(address, MidiController.convert_fader_to_hex(int(value)), token)

    def set_dca_switch_channel(self, token, dca_id, switch):
        dca = self.dcaDAO.get_dca_by_id(dca_id)

        if dca:
            address = [int(x, 16) for x in dca.midi_address.split(",")] + self.dca_switch_post
            self.midiController.send_command(address, MidiController.convert_switch_to_hex(switch), token)

    def load_scene(self, scene_id):

        self.midiController.load_scene(scene_id)

        return RedirectResponse(url="/mixer/home", status_code=303)

    def eq_set(self, token, channel, typeFreq, typeEQ, value):
        if channel:
            channel_address = self.channelDAO.get_channel_address(channel)
            if channel_address:
                address, data = get_eq_address_value(typeFreq, typeEQ, float(value))

                channel_address = [int(x, 16) for x in channel_address.split(',')]
                address = channel_address + address

                self.midiController.send_command(address, data, token)
        return None

    def eq_get(self, channel):
        if channel:
            channel_address = self.channelDAO.get_channel_address(channel)

            if channel_address:
                channel_address = [int(x, 16) for x in channel_address.split(',')]

                channelsQ = get_eq_channel(channel_address, call_type.Q)
                channelsFreq = get_eq_channel(channel_address, call_type.FREQ)
                channelsGain = get_eq_channel(channel_address, call_type.GAIN)

                #get Q values
                resultsValueQ = MidiListener.init_and_listen(list(channelsQ.values()) , call_type.Q)

                for keychannel, channel in channelsQ.items():
                    for key, ch in resultsValueQ.items():
                        if tuple(channel) == key:
                            channelsQ[keychannel] = resultsValueQ[key]

                #get Freq values
                resultsValueFreq = MidiListener.init_and_listen(list(channelsFreq.values()) , call_type.FREQ)

                for keychannel, channel in channelsFreq.items():
                    for key, ch in resultsValueFreq.items():
                        if tuple(channel) == key:
                            channelsFreq[keychannel] = resultsValueFreq[key]

                #get gain values
                resultsValueGain = MidiListener.init_and_listen(list(channelsGain.values()) , call_type.GAIN)

                for keychannel, channel in channelsGain.items():
                    for key, ch in resultsValueGain.items():
                        if tuple(channel) == key:
                            channelsGain[keychannel] = resultsValueGain[key]


                low = {}
                low_mid = {}
                mid_hi = {}
                high = {}

                low_mid["q"] = channelsQ["eq_low_mid_q"]
                mid_hi["q"] = channelsQ["eq_mid_hi_q"]

                low["freq"] = channelsFreq["eq_low_freq"]
                low_mid["freq"] = channelsFreq["eq_low_mid_freq"]
                mid_hi["freq"] = channelsFreq["eq_mid_hi_freq"]
                high["freq"] = channelsFreq["eq_high_freq"]

                low["gain"] = channelsGain["eq_low_gain"]
                low_mid["gain"] = channelsGain["eq_low_mid_gain"]
                mid_hi["gain"] = channelsGain["eq_mid_hi_gain"]
                high["gain"] = channelsGain["eq_high_gain"]

                combined = [low, low_mid, mid_hi, high]

                return json.dumps(combined, indent=3)

        return None

    def eq_switch_set(self, token, channel, switch):
        if channel:
            channel_address = self.channelDAO.get_channel_address(channel)
            if channel_address:
                
                channel_address = [int(x, 16) for x in channel_address.split(',')]
                address = channel_address + self.postEqSwitch

                data = MidiController.convert_switch_to_hex(not switch)

                self.midiController.send_command(address, data, token)
        return None
    
    def eq_switch_get(self, channel):
        if channel:
            channel_address = self.channelDAO.get_channel_address(channel)
            if channel_address:
                
                channel_address = [int(x, 16) for x in channel_address.split(',')]
                address = channel_address + self.postEqSwitch
                
                # channel request and listen
                resultsValue = MidiListener.init_and_listen([address], call_type.SWITCH)

                value = next(iter(resultsValue.values()))
                return not value

    def eq_preamp_set(self, token, channel, value):
        if channel and 0 <= value <= 55:
            channel_address = self.pre_preamp + [channel] + self.post_preamp
            self.midiController.send_command(channel_address, [value], token)

    def eq_preamp_get(self, channel):
        if channel:
            
            channel_address = self.channelDAO.get_channel_address(channel)

            if channel_address:

                channel_address = [int(x, 16) for x in channel_address.split(',')]
                channel_address[0] -= 1
                channel_address += self.postName

                resultsValue = MidiListener.init_and_listen([channel_address], call_type.PATCH_CHANNEL)

                value_patchbay = next(iter(resultsValue.values()))
                if 0 < value_patchbay < 80:
                    address_request = self.pre_preamp + [value_patchbay] + self.post_preamp
                    
                    # channel request and listen
                    resultsValue = MidiListener.init_and_listen([address_request], call_type.PREAMP)

                    value = next(iter(resultsValue.values()))
                else:
                    value_patchbay = -1
                    value = 0

                response = {
                    "ch_patch" : value_patchbay,
                    "preamp" : value
                }
                
                return json.dumps(response, indent=2)

    def set_fader_aux_value(self, token, auxId, canaleId, value):
        aux = self.auxDAO.get_aux_by_id(auxId)
        indirizzo = None
        if aux:
            if(canaleId == "main"):
                indirizzo = [int(x,16) for x in aux.midi_address_main.split(",")] + self.postMainFader
            else:
                address_aux = [int(x,16) for x in aux.midi_address.split(",")]

                canaleAddress = self.channelDAO.get_channel_address(canaleId)
                if canaleAddress:
                    channelAddresshex = [int(x,16) for x in canaleAddress.split(",")]

                    indirizzo = channelAddresshex + address_aux
            if indirizzo:
                self.midiController.send_command(indirizzo, MidiController.convert_fader_to_hex(int(value)), token)

    def set_switch_aux_value(self, token, auxId, canaleId, value):
        aux = self.auxDAO.get_aux_by_id(auxId)
        if aux:
            if(canaleId == "aux_main"):
                indirizzo = [int(x,16) for x in aux.midi_address_main.split(",")] + self.postSwitch
                self.midiController.send_command(indirizzo, MidiController.convert_switch_to_hex(int(value)), token)

    def save_disposition(self, disposition):
        with open(os.path.join(os.path.dirname(__file__), "..", "Database", "mixer_disposition.json"), "w", encoding="utf-8") as f:
            json.dump({"disposition": disposition}, f, indent=4, ensure_ascii=False)

    def load_disposition(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "Database", "mixer_disposition.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("disposition", [])