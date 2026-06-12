
from fastapi import APIRouter, Request
from auth.security import get_current_user
from dto.response.channel_layout_dto import ChannelLayoutDTO
from dto.request.create_profile_dto import CreateProfileDTO
from dto.response.profile_dto import ProfileDTO
from services.aux_service import AuxService
from services.user_service import UserService
from services.scene_service import SceneService

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

user_service = UserService()
scene_service = SceneService()
aux_service = AuxService()

# scene
@router.get("/scenes")
async def get_scenes(request: Request):
    user_data = get_current_user(request)

    return scene_service.get_all_user_scene(user_data["sub"])

# page scene
@router.get("/scene/{scene_id}")
async def load_scene(request: Request, scene_id: int):
    user_data = get_current_user(request)
    
    return user_service.load_scene(user_id= user_data["sub"], scene_id= scene_id)

@router.get("/aux/{aux_id}")
async def get_aux_values(request: Request, aux_id: int):
    user = get_current_user(request)

    return aux_service.load_fader_values(aux_id, None)

# Layout
@router.get("/scene/{scene_id}/layout")
async def get_channel_layout(request: Request, scene_id: int):
    user_data = get_current_user(request)

    return user_service.get_channel_layout(user_id = user_data["sub"], scene_id= scene_id)

@router.post("/scene/{scene_id}/layout")
async def set_channel_layout(request: Request, scene_id: int, layouts: list[ChannelLayoutDTO]):
    user_data = get_current_user(request)

    return user_service.set_channel_layout(user_id = user_data["sub"], scene_id= scene_id, layouts=layouts)


@router.put("/scene/{scene_id}/layout/default")
async def set_default_channel_layout(request: Request, scene_id: int):
    user_data = get_current_user(request)
    return user_service.set_default_layout(user_id = user_data["sub"], scene_id= scene_id)

# TODO valutare se servono
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


#Profile
@router.post("/scene/{scene_id}/profile")
async def create_profile(request : Request, scene_id : int, create_profile : CreateProfileDTO):
    user_data = get_current_user(request)

    return user_service.create_profile(user_data["sub"], scene_id, create_profile.profile, create_profile.faders)
    

@router.delete("/scene/{scene_id}/profile/{profile_id}")
async def delete_profile(request: Request, scene_id : int, profile_id : int):
    user_data = get_current_user(request)

    return user_service.delete_profile(profile_id, user_data["sub"], scene_id)
    
@router.delete("/scene/{scene_id}/profile")
async def delete_profiles(request: Request, scene_id : int):
    user_data = get_current_user(request)

    return user_service.delete_profiles(user_data["sub"], scene_id)

@router.put("/scene/{scene_id}/profile")
async def update_profile(request : Request, scene_id : int, update_profile: CreateProfileDTO):
    user_data = get_current_user(request)

    return user_service.update_profile(user_data["sub"], scene_id, update_profile.profile, update_profile.faders)


@router.get("/scene/{scene_id}/profile/{profile_id}/{aux_id}")
async def get_profile(request : Request, scene_id : int, profile_id: int, aux_id: int):
    user_data = get_current_user(request)
    token = request.cookies.get("access_token")

    return user_service.load_profile(user_data["sub"], token, scene_id, profile_id, aux_id)