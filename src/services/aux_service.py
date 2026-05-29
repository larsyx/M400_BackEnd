
from dao.aux_dao import AuxDAO
from dao.channel_dao import ChannelDAO
from dto.response.aux_dto import AuxDTO
from dto.response.fader_dto import FaderDTO
from midi.midi_controller import MidiController, MidiListener, call_type
from settings import POST_LINK, POST_MAIN_FADER, POST_NAME, POST_SWITCH, PRE_MAIN
from utils.utils import link_separation, string_to_hex_list


class AuxService:
    def __init__(self):
        self.channel_dao = ChannelDAO()
        self.aux_dao = AuxDAO()
        self.midi_controller = MidiController()

    def set_fader_value(self, token, aux_id, channel_id, value):
        aux = self.aux_dao.get_aux_by_id(aux_id)
        address = None
        if aux:
            if(channel_id == "Main"):
                address = string_to_hex_list(aux.midi_address_main) + POST_MAIN_FADER
            else:
                channel_address = self.channel_dao.get_channel_address(channel_id)
                if channel_address:
                    address = string_to_hex_list(channel_address) + string_to_hex_list(aux.midi_address)
            if address:
                self.midi_controller.send_command(address, MidiController.convert_db_to_hex(value), token)


    def set_switch_value(self, token, aux_id, channel_id, value):
        aux = self.aux_dao.get_aux_by_id(aux_id)
        if aux:
            if(channel_id == "Main"):
                address = string_to_hex_list(aux.midi_address_main) + POST_SWITCH
                self.midi_controller.send_command(address, MidiController.convert_switch_to_hex(int(value)), token)


    def load_fader_aux(self, aux_id):
        channels = self.channel_dao.get_all_channels()

        listen_address_fader = []
        listen_address_switch = []
        listen_address_name = []
        listen_address_link = []


        aux = self.aux_dao.get_aux_by_id(aux_id)
        if not aux:
            raise Exception("Aux inesistente")
        
        aux_addr_fader = string_to_hex_list(aux.midi_address)
        aux_addr_swich = string_to_hex_list(aux.midi_address_switch)
        aux_addr_main_fader = string_to_hex_list(aux.midi_address_main) + POST_MAIN_FADER
        aux_addr_main_switch = string_to_hex_list(aux.midi_address_main) + POST_SWITCH

        for channel in channels:
            
            channel_address = string_to_hex_list(channel.midi_address)
            
            listen_address_fader.append(channel_address + aux_addr_fader)
            listen_address_switch.append(channel_address + aux_addr_swich)
            listen_address_name.append(channel_address + POST_NAME)
            listen_address_link.append(channel_address + POST_LINK)

        listen_address_fader.append(aux_addr_main_fader)
        listen_address_switch.append(aux_addr_main_switch)

        # channel request and listen
        results_value = MidiListener.init_and_listen(listen_address_fader, call_type.CHANNEL)
        results_value_switch = MidiListener.init_and_listen(listen_address_switch, call_type.SWITCH)     
        results_value_name = MidiListener.init_and_listen(listen_address_name, call_type.NAME)       
        results_value_link = MidiListener.init_and_listen(listen_address_link, call_type.SWITCH)    

        fader_dto_list = []

        for channel in channels:
            channel_address = string_to_hex_list(channel.midi_address) 
            value = results_value.get((tuple(channel_address + aux_addr_fader)), 0)
            name = results_value_name.get((tuple(channel_address + POST_NAME)), channel.name)
            switch = results_value_switch.get((tuple(channel_address + aux_addr_swich)), False)
            link = results_value_link.get((tuple(channel_address + POST_LINK)), False)

            fader_dto_list.append(FaderDTO(id=channel.id, value=value, name=channel.name, description=name, switch=switch, link=link))

        fader_dto_list = link_separation(fader_dto_list)

        value_main = results_value.get((tuple(aux_addr_main_fader)), 0)
        switch_main = results_value_switch.get((tuple(aux_addr_main_switch)), False)

        fader_dto_list.append(FaderDTO(id=0, value=value_main, name="Main", switch=switch_main))

        return fader_dto_list
    
       
    def load_fader_aux_scene(self, aux_id, channels):
        listen_address_fader = []
        listen_address_switch = []
        listen_address_name = []


        aux = self.aux_dao.get_aux_by_id(aux_id)
        if not aux:
            raise Exception("Aux inesistente")
        
        aux_addr_fader = string_to_hex_list(aux.midi_address)
        aux_addr_swich = string_to_hex_list(aux.midi_address_switch)
        aux_addr_main_fader = string_to_hex_list(aux.midi_address_main) + POST_MAIN_FADER
        aux_addr_main_switch = string_to_hex_list(aux.midi_address_main) + POST_SWITCH

        for channel in channels:
            
            channel_address = string_to_hex_list(channel.channel.midi_address)
            
            listen_address_fader.append(channel_address + aux_addr_fader)
            listen_address_switch.append(channel_address + aux_addr_swich)
            listen_address_name.append(channel_address + POST_NAME)

        listen_address_fader.append(aux_addr_main_fader)
        listen_address_switch.append(aux_addr_main_switch)

        # channel request and listen
        results_value = MidiListener.init_and_listen(listen_address_fader, call_type.CHANNEL)
        results_value_switch = MidiListener.init_and_listen(listen_address_switch, call_type.SWITCH)     
        results_value_name = MidiListener.init_and_listen(listen_address_name, call_type.NAME)   

        fader_dto_list = []

        for channel in channels:
            channel_address = string_to_hex_list(channel.channel.midi_address) 
            value = results_value.get((tuple(channel_address + aux_addr_fader)), 0)
            name = results_value_name.get((tuple(channel_address + POST_NAME)), channel.channel.name)
            switch = results_value_switch.get((tuple(channel_address + aux_addr_swich)), False)

            fader_dto_list.append(FaderDTO(id=channel.channel.id, value=value, name=channel.channel.name, description=name, switch=switch, type=channel.type_channel))

        fader_dto_list = link_separation(fader_dto_list)

        value_main = results_value.get((tuple(aux_addr_main_fader)), 0)
        switch_main = results_value_switch.get((tuple(aux_addr_main_switch)), False)

        fader_dto_list.append(FaderDTO(id=0, value=value_main, name="Main", switch=switch_main))

        return fader_dto_list

    def load_aux_names(self):
        listen_address_aux_name = []
        auxs = self.aux_dao.get_all_aux()

        for aux in auxs:
            address = string_to_hex_list(aux.midi_address_main)
            listen_address_aux_name.append(address + POST_NAME)

        results_value_aux_name = MidiListener.init_and_listen(listen_address_aux_name, call_type.NAME) 
        aux_dto_list = []

        for aux in auxs:
            address = string_to_hex_list(aux.midi_address_main) 
            
            name = results_value_aux_name.get((tuple(address + POST_NAME)), aux.name)
            aux_dto_list.append(AuxDTO(id=aux.id, name=name))

        return aux_dto_list

    # TODO maybe load_fader_values