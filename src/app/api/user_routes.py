
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from app.dao.channel_dao import ChannelDAO
from app.dao.layout_canale_dao import LayoutCanaleDAO
from app.auth.security import get_current_user
from app.services.user_service import UserService
from app.services.scene_service import SceneService

router = APIRouter()

user_service = UserService()
scene_service = SceneService()

@router.get("/user/getScenes", response_class=HTMLResponse)
async def get_scenes(request: Request):
    user_data = get_current_user(request)

    return scene_service.get_all_user_scene(user_data["sub"], request)

    
@router.get("/user/scene_{scene_id}/", response_class=HTMLResponse)
async def load_scene(request: Request, scene_id: int):
    user_data = get_current_user(request)
    
    return user_service.load_scene(userID = user_data["sub"], scenaID = scene_id, request=request)


@router.get("/user/scene_{scene_id}/layout", response_class=HTMLResponse)
async def set_layout(request: Request, scene_id: int):
    user_data = get_current_user(request)

    return user_service.set_layout(userID = user_data["sub"], scenaID = scene_id, request=request)


@router.post("/user/scene_{scene_id}/set")
async def set_fader(request: Request):
    user_data = get_current_user(request)
    token = request.cookies.get("access_token")

    data = await request.json()
    canaleId = data.get("canaleId")
    value = data.get("value")
    indirizzoAux = data.get("aux")

    user_service.set_fader(token, canaleId, value, indirizzoAux)
    
@router.get("/user/scene_{scene_id}/getAux/{aux_id}")
async def get_aux(request: Request, aux_id: int):
    user_data = get_current_user(request)

    return user_service.get_aux(aux_id)


@router.post("/user/scene_{scene_id}/set/main")
async def set_fader_main(request: Request):
    user_data = get_current_user(request)
    token = request.cookies.get("access_token")

    data = await request.json()
    value = data.get("value")
    indirizzoAux = data.get("aux")
    
    user_service.set_fader_main(token, value, indirizzoAux)
   
@router.post("/user/scene_{scene_id}/layout/addChannelLayout")
async def add_channel_Layout(request: Request, scene_id: int):
    user_data = get_current_user(request)
    

    layoutDAO = LayoutCanaleDAO()
    data = await request.json()
    layoutDAO.add_layout_channel(user_data["sub"], scene_id, data.get("canale_id"), data.get("descrizione"))

    return True


@router.post("/user/scene_{scene_id}/layout/removeChannelLayout")
async def remove_channel_layout(request: Request, scene_id: int):
    user_data = get_current_user(request)

    layoutDAO = LayoutCanaleDAO()
    data = await request.json()
    canale_id = data.get("canale_id")

    layoutDAO.remove_layout_channel(user_data["sub"], scene_id, canale_id)

    channelDAO = ChannelDAO()
    channel = channelDAO.get_channel_by_id(canale_id)
    return f"{channel.name} : {channel.description}"

    
@router.post("/user/scene_{scene_id}/layout/updateLayout")
async def set_layouts(request: Request, scene_id : int):
    user_data = get_current_user(request)
    
    layoutDAO = LayoutCanaleDAO()   
    data = await request.json()

    channelslayout = data.get("channelsLayout")

    for layout in channelslayout:
        layoutDAO.set_layout_channel(user_data["sub"], scene_id, layout.get("canaleId"), layout.get("posizione"), layout.get("descrizione"), layout.get("isBatteria"))

    return "Layout salvato con successo"

@router.get("/user/scene_{scene_id}/getFadersValue")
async def get_fader_value(request: Request, scene_id : int, aux: str, auxMain: str):

    user_data = get_current_user(request)

    return user_service.get_faders_value(user_data["sub"], scene_id, aux, auxMain)

@router.post("/user/scene_{scene_id}/getNamesValue")
async def get_names_value(request: Request, scene_id : int):
    user_data = get_current_user(request)

    data = await request.json()
    list_channels = data.get("list_channels")

    return user_service.get_faders_names(list_channels)


@router.post("/user/scene_{scene_id}/createProfile")
async def create_profile(request : Request, scene_id : int):
    user_data = get_current_user(request)

    data = await request.json()
    name = data.get("name")
    profiles = data.get("profiles")

    return user_service.create_profile(name, user_data["sub"], scene_id, profiles)
    

@router.delete("/user/scene_{scene_id}/deleteProfile")
async def delete_profile(request: Request, scene_id : int, profile_id : int):
    user_data = get_current_user(request)

    return user_service.delete_profile(profile_id, user_data["sub"], scene_id)
    
@router.delete("/user/scene_{scene_id}/deleteProfiles")
async def delete_profiles(request: Request, scene_id : int):
    user_data = get_current_user(request)

    return user_service.delete_profiles(user_data["sub"], scene_id)

@router.put("/user/scene_{scene_id}/updateProfile")
async def update_profile(request : Request, scene_id : int):
    user_data = get_current_user(request)

    data = await request.json()
    profile_id = data.get("id")
    profiles = data.get("profiles")

    return user_service.update_profile(profile_id, user_data["sub"], scene_id, profiles)


@router.get("/user/scene_{scene_id}/getProfile")
async def get_profile(request : Request, scene_id : int, profile_id: int):
    user_data = get_current_user(request)
    token = request.cookies.get("access_token")

    return user_service.load_profile(user_data["sub"], token, scene_id, profile_id)


