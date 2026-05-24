import json
import os
from fastapi.responses import RedirectResponse
from dao.channel_dao import ChannelDAO
from dao.dca_dao import DCA_DAO
from dao.aux_dao import AuxDAO
from dto.response.aux_dto import AuxDTO
from dto.response.fader_dto import FaderDTO
from midi.midi_controller import MidiController, MidiListener, call_type, get_eq_address_value, get_eq_channel
from settings import POST_MAIN_FADER, POST_SWITCH, PRE_MAIN, POST_EQ_SWITCH, POST_NAME, POST_LINK, PRE_PREAMP, POST_PREAMP, DCA_FADER_POST, DCA_SWITCH_POST
from utils.utils import link_separation, string_to_hex_list


class MixerService:
    def __init__(self):
        self.channel_dao = ChannelDAO()
        self.dca_dao = DCA_DAO()
        self.aux_dao = AuxDAO()
        self.midi_controller = MidiController()

    def load_fader(self):
        channels = self.channel_dao.get_all_channels()

        order = self.load_disposition()

        # get value canali
        listen_address_fader = []
        listen_address_switch = []
        listen_address_name = []
        listen_address_link = []

        # initialize the list of addresses for request and listen
        for channel in channels:
            channel_address = [int(x,16) for x in channel.midi_address.split(",")] 
            
            listen_address_fader.append(channel_address + POST_MAIN_FADER)
            listen_address_switch.append(channel_address + POST_SWITCH)
            listen_address_name.append(channel_address + POST_NAME)
            listen_address_link.append(channel_address + POST_LINK)

        listen_address_fader.append(PRE_MAIN + POST_MAIN_FADER)
        listen_address_switch.append(PRE_MAIN + POST_SWITCH)

        # channel request and listen
        results_value = MidiListener.init_and_listen(listen_address_fader, call_type.CHANNEL)
        results_value_switch = MidiListener.init_and_listen(listen_address_switch, call_type.SWITCH)     
        results_value_name = MidiListener.init_and_listen(listen_address_name, call_type.NAME)       
        results_value_link = MidiListener.init_and_listen(listen_address_link, call_type.SWITCH)    

        fader_dto_list = []

        for channel in channels:
            channel_address = [int(x,16) for x in channel.midi_address.split(",")] 
            value = results_value.get((tuple(channel_address + POST_MAIN_FADER)), 0)
            name = results_value_name.get((tuple(channel_address + POST_NAME)), channel.name)
            switch = results_value_switch.get((tuple(channel_address + POST_SWITCH)), False)
            link = results_value_link.get((tuple(channel_address + POST_LINK)), False)

            fader_dto_list.append(FaderDTO(id=channel.id, value=value, name=channel.name, description=name, switch=switch, link=link))

        fader_dto_list = link_separation(fader_dto_list)

        value_main = results_value.get((tuple(PRE_MAIN + POST_MAIN_FADER)), 0)
        switch_main = results_value_switch.get((tuple(PRE_MAIN + POST_SWITCH)), False)

        fader_dto_list.append(FaderDTO(id=0, value=value_main, name="Main", switch=switch_main))

        return fader_dto_list
    

    def load_dca(self):
        dcas = self.dca_dao.get_dca()

        # get value canali
        listen_address_fader = []
        listen_address_switch = []
        listen_address_name = []

        # initialize the list of addresses for request and listen
        for dca in dcas:
            dca_address = [int(x,16) for x in dca.midi_address.split(",")] 
            
            listen_address_fader.append(dca_address + POST_MAIN_FADER)
            listen_address_switch.append(dca_address + POST_SWITCH)
            listen_address_name.append(dca_address + POST_NAME)

                # channel request and listen
        results_value = MidiListener.init_and_listen(listen_address_fader, call_type.CHANNEL)
        results_value_switch = MidiListener.init_and_listen(listen_address_switch, call_type.SWITCH)     
        results_value_name = MidiListener.init_and_listen(listen_address_name, call_type.NAME)

        dca_dto_list = []

        for dca in dcas:
            dca_address = [int(x,16) for x in dca.midi_address.split(",")] 
            value = results_value.get((tuple(dca_address + POST_MAIN_FADER)), 0)
            name = results_value_name.get((tuple(dca_address + POST_NAME)), dca.name)
            switch = results_value_switch.get((tuple(dca_address + POST_SWITCH)), False)

            dca_dto_list.append(FaderDTO(id=dca.id, value=value, name=dca.name, description=name, switch=switch))

        return dca_dto_list
    
    def load_aux_names(self):
        listen_address_aux_name = []
        auxs = self.aux_dao.get_all_aux()

        for aux in auxs:
            address = [int(x,16) for x in aux.midi_address_main.split(",")]
            listen_address_aux_name.append(address + POST_NAME)

        results_value_aux_name = MidiListener.init_and_listen(listen_address_aux_name, call_type.NAME) 
        aux_dto_list = []

        for aux in auxs:
            address = [int(x,16) for x in aux.midi_address_main.split(",")] 
            
            name = results_value_aux_name.get((tuple(address + POST_NAME)), aux.name)
            aux_dto_list.append(AuxDTO(id=aux.id, name=name))

        return aux_dto_list

    def load_scenes(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "Database", "scenes.json"), "r") as file:
            scene = json.load(file)

        return scene.get('scenes', [])

    def load_scene(self, scene_id):
        self.midi_controller.load_scene(scene_id)

    def get_aux_parameters(self, aux_id):
        aux = self.aux_dao.get_aux_by_id(aux_id)
        channels = self.channel_dao.get_all_channels()
        if aux and channels:
            address_aux = [int(x, 16) for x in aux.midi_address.split(",")]

            aux_addresses_fader = []
            for channel in channels:
                channel_address = [int(x, 16) for x in channel.midi_address.split(",")]
                aux_addresses_fader.append(channel_address + address_aux)

            aux_address = [int(x,16) for x in aux.midi_address_main.split(",")] 
            aux_addresses_fader.append(aux_address + POST_MAIN_FADER)
            
            results_value = MidiListener.init_and_listen(aux_addresses_fader, call_type.CHANNEL)
            result_switch_main = MidiListener.init_and_listen([[int(x,16) for x in aux.midi_address_main.split(",")] + POST_SWITCH], call_type.SWITCH)

            fader_dto_list = []

            for channel in channels:
                channel_address = [int(x,16) for x in channel.midi_address.split(",")] 
                value = results_value.get((tuple(channel_address + address_aux)), 0)
                fader_dto_list.append(FaderDTO(id=channel.id, name=channel.name, description=channel.name, value=value, switch=False, link=False))

            value = results_value.get((tuple(aux_address + POST_MAIN_FADER)), 0)
            switch = next(iter(result_switch_main.values()), False)
            fader_dto_list.append(FaderDTO(id=0, name='Main', description='Main', value=value, switch=switch, link=False))

            return fader_dto_list

        return None

    def set_fader_value(self, token, channel_id, value):
        if channel_id == 0:
            address = PRE_MAIN + POST_MAIN_FADER
        else: 
            channel_address = self.channel_dao.get_channel_address(channel_id)
            channel_address_hex = string_to_hex_list(channel_address)
            address = channel_address_hex + POST_MAIN_FADER

        if address:
            self.midi_controller.send_command(address, MidiController.convert_db_to_hex(value), token)

    def set_switch_channel(self, token, channel_id, switch):
        if channel_id == 'Main':
            address = PRE_MAIN + POST_MAIN_FADER

        else:
            channel_address = self.channel_dao.get_channel_address(channel_id)
            address = string_to_hex_list(channel_address) + POST_SWITCH
            
        if address:
            self.midi_controller.send_command(address, MidiController.convert_switch_to_hex(switch), token)

    def set_dca_fader_value(self, token, dca_id, value):
        dca = self.dca_dao.get_dca_by_id(dca_id)

        if dca:
            address = string_to_hex_list(dca.midi_address) + DCA_FADER_POST
            self.midi_controller.send_command(address, MidiController.convert_db_to_hex(value), token)

    def set_dca_switch_channel(self, token, dca_id, switch):
        dca = self.dca_dao.get_dca_by_id(dca_id)

        if dca:
            address = string_to_hex_list(dca.midi_address) + DCA_SWITCH_POST
            self.midi_controller.send_command(address, MidiController.convert_switch_to_hex(switch), token)

    def eq_set(self, token, channel, typeFreq, typeEQ, value):
        if channel:
            channel_address = self.channel_dao.get_channel_address(channel)
            if channel_address:
                address, data = get_eq_address_value(typeFreq, typeEQ, float(value))

                channel_address = [int(x, 16) for x in channel_address.split(',')]
                address = channel_address + address

                self.midi_controller.send_command(address, data, token)
        return None

    def eq_get(self, channel):
        if channel:
            channel_address = self.channel_dao.get_channel_address(channel)

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
            channel_address = self.channel_dao.get_channel_address(channel)
            if channel_address:
                
                channel_address = [int(x, 16) for x in channel_address.split(',')]
                address = channel_address + POST_EQ_SWITCH

                data = MidiController.convert_switch_to_hex(not switch)

                self.midi_controller.send_command(address, data, token)
        return None
    
    def eq_switch_get(self, channel):
        if channel:
            channel_address = self.channel_dao.get_channel_address(channel)
            if channel_address:
                
                channel_address = [int(x, 16) for x in channel_address.split(',')]
                address = channel_address + POST_EQ_SWITCH
                
                # channel request and listen
                resultsValue = MidiListener.init_and_listen([address], call_type.SWITCH)

                value = next(iter(resultsValue.values()))
                return not value

    def eq_preamp_set(self, token, channel, value):
        if channel and 0 <= value <= 55:
            channel_address = PRE_PREAMP + [channel] + POST_PREAMP
            self.midi_controller.send_command(channel_address, [value], token)

    def eq_preamp_get(self, channel):
        if channel:
            
            channel_address = self.channel_dao.get_channel_address(channel)

            if channel_address:

                channel_address = [int(x, 16) for x in channel_address.split(',')]
                channel_address[0] -= 1
                channel_address += POST_NAME

                resultsValue = MidiListener.init_and_listen([channel_address], call_type.PATCH_CHANNEL)

                value_patchbay = next(iter(resultsValue.values()))
                if 0 < value_patchbay < 80:
                    address_request = PRE_PREAMP + [value_patchbay] + POST_PREAMP
                    
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

    def save_disposition(self, disposition):
        with open(os.path.join(os.path.dirname(__file__), "..", "Database", "mixer_disposition.json"), "w", encoding="utf-8") as f:
            json.dump({"disposition": disposition}, f, indent=4, ensure_ascii=False)

    def load_disposition(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "Database", "mixer_disposition.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("disposition", [])