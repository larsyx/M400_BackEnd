from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from services.ws_service import MsgType, WsConnectionState, WsRole, WsService

router = APIRouter()
ws_service = WsService()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.websocket("/ws/liveSyncAux")
async def live_aux(websocket: WebSocket):
    await websocket.accept()

    state = WsConnectionState()
    sync = None

    try:
        data = await websocket.receive_json()
        logger.info(f"[aux ws] <-- {data}")

        if data.get("type") != MsgType.AUTH:
            logger.warning(f"non AUTH (type={data.get('type')}), chiudo")
            await websocket.close(code=1008)
            return

        payload = data.get("payload") or {}
        try:
            role = WsRole(payload.get("role"))
        except ValueError:
            await websocket.close(code=1008)
            return

        session_id, user_id = ws_service.authenticate(payload, role)
        aux_id = ws_service.resolve_aux_id(role, payload)
        send_back = ws_service.make_aux_ws_sendback(role, websocket, state)
        sync = ws_service.build_aux_ws_sync(role, session_id, send_back, aux_id)
        state.authenticated = True
        logger.info(f"autenticato user={user_id} role={role.value}")

        while True:
            data = await websocket.receive_json()
            response = ws_service.handle_aux_message(data, session_id, aux_id)
            if response is not None:
                await websocket.send_json(response)

    except WebSocketDisconnect:
        print("Il client ha chiuso la connessione.")
    finally:
        if sync:
            sync.stop()
        state.is_active = False


@router.websocket("/ws/liveSyncMixer")
async def live_mixer(websocket: WebSocket):
    await websocket.accept()

    state = WsConnectionState()
    send_back = ws_service.make_mixer_sendback(websocket, state)
    session_id = None
    sync = None

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if not state.authenticated:
                if msg_type == MsgType.AUTH:
                    payload = data.get("payload") or {}
                    session_id, user_id = ws_service.authenticate(payload, WsRole.MIXER)
                    sync = ws_service.build_mixer_sync(
                        session_id, send_back, aux_id=payload.get("aux_id")
                    )
                    state.authenticated = True
                    logger.info(f"auth user={user_id}")
                else:
                    await websocket.close(code=1008)
                    return
                continue

            response = ws_service.handle_mixer_message(data, session_id)
            if response is not None:
                logger.info(f"[mixer ws] --> {response}")
                await websocket.send_json(response)

    except WebSocketDisconnect:
        print("Il client ha chiuso la connessione.")
    finally:
        if sync:
            sync.stop()
        state.is_active = False
