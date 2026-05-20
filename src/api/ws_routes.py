from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from dao.dca_dao import DCA_DAO
from auth.security import get_current_user_token, verify_mixer, verify_video
from midi.midi_controller import MidiMixerSync, MidiUserSync, MidiVideoSync
from dao.channel_dao import ChannelDAO
from dao.aux_dao import AuxDAO
import os
from dotenv import load_dotenv
from services.mixer_service import MixerService
from settings import PRE_DCA
from enum import Enum

router = APIRouter()

mixer_service = MixerService()


class MsgType(str, Enum):
    AUTH = "auth"
    PING = "ping"
    SLIDER_VALUE = "slider_value"
    SLIDER_SWITCH = "slider_switch"
    DCA_VALUE = "dca_value"
    DCA_SWITCH = "dca_switch"



@router.websocket("/ws/liveSync")
async def live_user(websocket: WebSocket):
    cookies = websocket.cookies
    session_id = cookies.get("access_token")
    user_id = get_current_user_token(session_id)

    await websocket.accept()

    is_active=True

    async def send_back(channel_address, value):
        try:
            if is_active:
                channelDAO = ChannelDAO()

                if(channel_address == 'main'):
                    channel = channel_address
                else:
                    channel = channelDAO.get_channel_by_address(channel_address).id
                

                response = {
                    "channel" : channel,
                    "value" : value
                }

                await websocket.send_json(response)
        except Exception as e:
            print(f"errore sync {e}")


    sync = None

    try:
        while True:
            data = await websocket.receive_json()
            add = data.get("address")
            addMain = data.get("addressMain")
            address = [int(val,0) for val in add.split(",")]
            addressMain = [int(val,0) for val in addMain.split(",")]
            if address:
                sync = MidiUserSync(sendback=send_back, address=address, addressMain=addressMain, token_user=session_id)
                address = None
            
    except WebSocketDisconnect:
        print("Il client ha chiuso la connessione.")
    finally:
        if sync:
            sync.stop()
        is_active = False      



@router.websocket("/ws/liveSyncMixer")
async def live_mixer(websocket: WebSocket):

    await websocket.accept()

    is_active = True
    authenticated = False
    session_id = None
    user_id = None
    sync = None

    async def send_back(type, channel_address, value):
        try:
            if is_active and authenticated:
                dca = False

                if channel_address == 'main':
                    channel = channel_address

                elif int(channel_address[0:4], 16) == PRE_DCA:
                    dcaDAO = DCA_DAO()
                    channel = dcaDAO.get_dca_by_address(channel_address)
                    channel = channel.id
                    dca = True

                else:
                    channelDAO = ChannelDAO()
                    channel = channelDAO.get_channel_by_address(channel_address)
                    channel = channel.id

                if channel:
                    response = {
                        "type": type,
                        "payload": {
                            "dca": dca,
                            "channel": channel,
                            "value": value
                        }
                    }

                    await websocket.send_json(response)
        except Exception as e:
            print(f"errore liveSyncMixer {e}")

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            payload = data.get("payload")


            if not authenticated:
                if msg_type == MsgType.AUTH:
                    session_id = payload.get("token")

                    user_id = get_current_user_token(session_id)
                    verify_mixer(user_id["sub"])

                    sync = MidiMixerSync(
                        send_back=send_back,
                        token_user=session_id
                    )

                    authenticated = True
                    print("✅ WebSocket autenticata")

                else:
                    await websocket.close(code=1008)
                    return

                continue

            if msg_type == MsgType.SLIDER_VALUE:
                print(data)
                channel = payload.get("channel")
                value = payload.get("value")

                mixer_service.set_fader_value(session_id, channel, float(value))

            elif msg_type == MsgType.PING:
                await websocket.send_json({
                    "type": "pong",
                    "payload": {}
                })

    except WebSocketDisconnect:
        print("Il client ha chiuso la connessione.")
        
    finally:
        if sync:
            sync.stop()
        is_active = False


@router.websocket("/ws/liveMixerSync/aux/{aux_id}")
async def live_aux_mixer(websocket: WebSocket, aux_id: int):
    cookies = websocket.cookies
    session_id = cookies.get("access_token")
    user_id = get_current_user_token(session_id)
    verify_mixer(user_id["sub"])

    await websocket.accept()

    is_active=True

    async def send_back(type, channel_address, value):
        try:
            if is_active:
                channelDAO = ChannelDAO()

                if(channel_address == 'main'):
                    channel = channel_address
                else:
                    channel = channelDAO.get_channel_by_address(channel_address).id
                
                response = {
                    "type" : type,
                    "channel" : channel,
                    "value" : value
                }

                await websocket.send_json(response)
        except Exception as e:
            print(f"errore sync {e}")

    auxDAO = AuxDAO()
    aux = auxDAO.get_aux_by_id(aux_id)
    address = [int(val,0) for val in aux.midi_address.split(",")]
    addressMain = [int(val,0) for val in aux.midi_address_main.split(",")]
    sync = MidiVideoSync(sendback=send_back, address=address, addressMain=addressMain, token_user=session_id)
                

    try:
        while True:
            data = await websocket.receive_json()
            
    except WebSocketDisconnect:
        print("Il client ha chiuso la connessione.")
    finally:
        if sync:
            sync.stop()
        is_active = False      



@router.websocket("/ws/liveSyncVideo")
async def live_video(websocket: WebSocket):

    cookies = websocket.cookies
    session_id = cookies.get("access_token")
    user_id = get_current_user_token(session_id)
    verify_video(user_id["sub"])

    await websocket.accept()

    is_active=True

    async def send_back(type, channel_address, value):
        try:
            if is_active:

                if channel_address == 'main':
                    channel = channel_address
                else:
                    channelDAO = ChannelDAO()
                    channel = channelDAO.get_channel_by_address(channel_address)
                    channel = channel.id
                
                if channel:
                    response = {
                        "type" : type,
                        "channel" : channel,
                        "value" : value
                    }

                    await websocket.send_json(response)
        except Exception as e:
                print(f"errore liveSyncVideo {e}")
            
    load_dotenv()
    auxdao = AuxDAO()
    auxId = os.getenv("VIDEO_AUX_ID")
    aux = auxdao.get_aux_by_id(int(auxId))

    if(aux):
        address = [int(val,0) for val in aux.midi_address.split(",")]
        addressMain = [int(val,0) for val in aux.midi_address_main.split(",")]

    sync = MidiVideoSync(sendback=send_back, address=address, addressMain=addressMain, token_user=session_id)

    try:
        while True:
            await websocket.receive_json()
            
    except WebSocketDisconnect:
        print("Il client ha chiuso la connessione.")
    finally:
        if sync:
            sync.stop()
        is_active = False  

