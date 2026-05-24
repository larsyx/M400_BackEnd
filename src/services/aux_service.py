
from dao.aux_dao import AuxDAO
from dao.channel_dao import ChannelDAO
from midi.midi_controller import MidiController
from settings import POST_MAIN_FADER, POST_SWITCH
from utils.utils import string_to_hex_list


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
