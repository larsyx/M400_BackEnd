import os
from enum import Enum

from dotenv import load_dotenv
from fastapi import WebSocket

from auth.security import get_current_user_token, verify_mixer, verify_video
from dao.aux_dao import AuxDAO
from dao.channel_dao import ChannelDAO
from dao.dca_dao import DCA_DAO
from midi.midi_controller import MidiMixerSync, MidiUserSync, MidiVideoSync
from services.aux_service import AuxService
from services.mixer_service import MixerService
from services.user_service import UserService
from services.video_service import VideoService
from settings import PRE_DCA
from utils.hex_utils import string_to_hex_list


class MsgType(str, Enum):
    AUTH = "auth"
    PING = "ping"
    SLIDER_VALUE = "slider_value"
    SLIDER_SWITCH = "slider_switch"
    DCA_VALUE = "dca_value"
    DCA_SWITCH = "dca_switch"


class WsRole(str, Enum):
    USER = "user"
    MIXER = "mixer"
    VIDEO = "video"


class WsConnectionState:
    def __init__(self):
        self.is_active = True
        self.authenticated = False


class WsService:
    def __init__(self):
        self.channel_dao = ChannelDAO()
        self.dca_dao = DCA_DAO()
        self.aux_dao = AuxDAO()
        self.mixer_service = MixerService()
        self.user_service = UserService()
        self.video_service = VideoService()
        self.aux_service = AuxService()

    def resolve_channel(self, channel_address, allow_dca=False):
        if channel_address == 'main':
            return 'main', False

        if allow_dca and int(channel_address[0:4], 16) == PRE_DCA[0]:
            dca = self.dca_dao.get_dca_by_address(channel_address)
            return (dca.id if dca else None), True

        channel = self.channel_dao.get_channel_by_address(channel_address)
        return (channel.id if channel else None), False

    def make_user_sendback(self, websocket: WebSocket, state: WsConnectionState):
        async def send_back(channel_address, value):
            try:
                if state.is_active and state.authenticated:
                    channel_id, _ = self.resolve_channel(channel_address)
                    await websocket.send_json({"channel": channel_id, "value": value})
            except Exception as e:
                print(f"errore sync {e}")
        return send_back

    def make_mixer_sendback(self, websocket: WebSocket, state: WsConnectionState):
        async def send_back(type, channel_address, value):
            try:
                if state.is_active and state.authenticated:
                    channel_id, dca = self.resolve_channel(channel_address, allow_dca=True)
                    if channel_id:
                        await websocket.send_json({
                            "type": type,
                            "payload": {
                                "dca": dca,
                                "channel": channel_id,
                                "value": value,
                            },
                        })
            except Exception as e:
                print(f"errore liveSyncMixer {e}")
        return send_back

    def make_aux_sendback(self, websocket: WebSocket, state: WsConnectionState):
        async def send_back(type, channel_address, value):
            try:
                if state.is_active and state.authenticated:
                    channel_id, _ = self.resolve_channel(channel_address)
                    await websocket.send_json({
                        "type": type,
                        "channel": channel_id,
                        "value": value,
                    })
            except Exception as e:
                print(f"errore sync {e}")
        return send_back

    def make_video_sendback(self, websocket: WebSocket, state: WsConnectionState):
        async def send_back(type, channel_address, value):
            try:
                if state.is_active and state.authenticated:
                    channel_id, _ = self.resolve_channel(channel_address)
                    if channel_id:
                        await websocket.send_json({
                            "type": type,
                            "channel": channel_id,
                            "value": value,
                        })
            except Exception as e:
                print(f"errore liveSyncVideo {e}")
        return send_back

    def authenticate(self, payload, role: WsRole):
        session_id = payload.get("token")
        user_token = get_current_user_token(session_id)
        user_id = user_token["sub"]

        if role == WsRole.MIXER:
            verify_mixer(user_id)
        elif role == WsRole.VIDEO:
            verify_video(user_id)

        return session_id, user_id

    def build_mixer_sync(self, session_id, send_back, aux_id=None):
        if aux_id:
            aux = self.aux_dao.get_aux_by_id(aux_id)
            address = string_to_hex_list(aux.midi_address)
            address_main = aux.midi_address(aux.midi_address_main)
            return MidiVideoSync(
                sendback=send_back,
                address=address,
                addressMain=address_main,
                token_user=session_id,
            )
        return MidiMixerSync(send_back=send_back, token_user=session_id)

    def build_aux_sync(self, session_id, send_back, aux_id):
        aux = self.aux_dao.get_aux_by_id(aux_id)
        address = string_to_hex_list(aux.midi_address)
        address_main = string_to_hex_list(aux.midi_address_main)
        return MidiVideoSync(
            sendback=send_back,
            address=address,
            addressMain=address_main,
            token_user=session_id,
        )

    def get_video_aux_id(self):
        load_dotenv()
        return int(os.getenv("VIDEO_AUX_ID"))

    def build_video_sync(self, session_id, send_back, aux_id):
        aux = self.aux_dao.get_aux_by_id(aux_id)
        address = string_to_hex_list(aux.midi_address)
        address_main = string_to_hex_list(aux.midi_address_main)
        return MidiVideoSync(
            sendback=send_back,
            address=address,
            addressMain=address_main,
            token_user=session_id,
        )

    def build_user_sync(self, session_id, send_back, aux_id):
        aux = self.aux_dao.get_aux_by_id(aux_id)
        address = string_to_hex_list(aux.midi_address)
        address_main = string_to_hex_list(aux.midi_address_main)
        return MidiUserSync(
            sendback=send_back,
            address=address,
            addressMain=address_main,
            token_user=session_id,
        )

    def make_aux_ws_sendback(self, role: WsRole, websocket: WebSocket, state: WsConnectionState):
        if role == WsRole.USER:
            return self.make_user_sendback(websocket, state)
        if role == WsRole.VIDEO:
            return self.make_video_sendback(websocket, state)
        return self.make_aux_sendback(websocket, state)

    def build_aux_ws_sync(self, role: WsRole, session_id, send_back, aux_id):
        if role == WsRole.USER:
            return self.build_user_sync(session_id, send_back, aux_id)
        if role == WsRole.VIDEO:
            return self.build_video_sync(session_id, send_back, aux_id)
        return self.build_aux_sync(session_id, send_back, aux_id)

    def resolve_aux_id(self, role: WsRole, payload):
        if role == WsRole.VIDEO:
            return self.get_video_aux_id()
        return payload.get("aux_id")

    def handle_aux_message(self, data, session_id, aux_id):
        msg_type = data.get("type")
        payload = data.get("payload") or {}

        match msg_type:
            case MsgType.SLIDER_VALUE:
                self.aux_service.set_fader_value(
                    session_id, aux_id, payload.get("channel"), float(payload.get("value"))
                )

            case MsgType.SLIDER_SWITCH:
                self.aux_service.set_switch_value(
                    session_id, aux_id, payload.get("channel"), bool(payload.get("value"))
                )

            case MsgType.PING:
                return {"type": "pong", "payload": {}}

        return None

    def handle_mixer_message(self, data, session_id):
        msg_type = data.get("type")
        payload = data.get("payload") or {}

        match msg_type:
            case MsgType.SLIDER_VALUE:
                self.mixer_service.set_fader_value(
                    session_id, payload.get("channel"), float(payload.get("value"))
                )

            case MsgType.SLIDER_SWITCH:
                self.mixer_service.set_switch_channel(
                    session_id, payload.get("channel"), bool(payload.get("value"))
                )

            case MsgType.DCA_VALUE:
                self.mixer_service.set_dca_fader_value(
                    session_id, payload.get("channel"), float(payload.get("value"))
                )

            case MsgType.DCA_SWITCH:
                self.mixer_service.set_dca_switch_channel(
                    session_id, payload.get("channel"), bool(payload.get("value"))
                )

            case MsgType.PING:
                return {"type": "pong", "payload": {}}

        return None
