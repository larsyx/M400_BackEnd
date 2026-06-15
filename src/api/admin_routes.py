from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from auth.security import get_current_user, verify_admin
from dto.request.admin_scene_dto import AdminSceneDTO
from dto.request.user_dto import UserDTO
from dto.response.channel_layout_dto import ChannelLayoutDTO
from dto.response.scene_dto import SceneDTO
from services.admin_service import AdminService
from services.scene_service import SceneService 
router = APIRouter(
    prefix="/admin"
)

scene_service = SceneService()
admin_service = AdminService()


# user manage
@router.get("/user")
async def get_all_users(request: Request):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return admin_service.get_users(user["sub"])

@router.post("/user")
async def create_user(request: Request, new_user: UserDTO):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return admin_service.create_user(user["sub"], new_user)

@router.put("/user/{username}")
async def update_user(request: Request, username: str, new_user: UserDTO):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return admin_service.update_user(user["sub"], username, new_user)


@router.delete("/user/{user_id}")
async def delete_user(request : Request, user_id):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return admin_service.delete_user(user["sub"], user_id)

#scene manage   
@router.get("/scene")
async def get_scenes(request: Request):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return scene_service.get_scenes(user["sub"])

@router.get("/scene/{scene_id}")
async def get_scenes(request: Request, scene_id: int):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return scene_service.get_scene_by_id(user["sub"], scene_id)

@router.post("/scene")
async def create_scene(request : Request, scene: SceneDTO):
    user = get_current_user(request)
    verify_admin(user["sub"])
    return scene_service.create_scene(user["sub"], scene)


@router.post("/scene/{scene_id}")
async def delete_scene(request : Request, scene_id : int):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return scene_service.delete_scene(user["sub"], scene_id)

@router.delete("/scene/{scene_id}")
async def delete_scene(request : Request, scene_id : int):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return scene_service.delete_scene(user["sub"], scene_id)

@router.put("/scene/{scene_id}")
async def update_scene(request : Request, scene : AdminSceneDTO):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return scene_service.update_scene(user["sub"], scene)



#manage user scene
@router.post("/scene/{scene_id}/user")
async def add_participants_scene(request : Request, scene_id : int, username : str = Form(...), aux : str = Form(...)):
    user = get_current_user(request)
    verify_admin(user["sub"])
    
    return scene_service.add_partecipante(request, user["sub"], scene_id, username, aux)

@router.delete("/scene/{scene_id}/user")
async def remove_participants_scene(request : Request, scene_id : int, username : str = Form(...)):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return scene_service.remove_partecipante(request, user["sub"], scene_id, username)

@router.put("/scene/{scene_id}/user")
async def change_aux(request: Request, scene_id : int):
    user = get_current_user(request)
    verify_admin(user["sub"])

    data = await request.json()
    user = data.get("user")
    aux = data.get("aux")

    admin_service.change_aux_user(user, aux, scene_id)

# manage channel
@router.get("/admin/manageChannels", response_class=HTMLResponse)
async def manage_user(request: Request):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return admin_service.load_manage_channels(request, user["sub"])

@router.post("/admin/manageChannels/changeDescription")
async def change_description(request: Request):
    user = get_current_user(request)
    verify_admin(user["sub"])

    data = await request.json()
    typeReq = data.get("type")
    id = data.get("id")
    value = data.get("value")

    return admin_service.change_description(user["sub"], typeReq, id, value)


# manage mixer scene
@router.get("/admin/manageSceneMixer")
async def manage_scene_mixer(request: Request):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return admin_service.load_mixer_scene(request)

@router.post("/admin/addMixerScene")
async def add_mixer_scene(request: Request, idScene: int = Form(...), name: str = Form(...)):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return admin_service.add_mixer_scene(request, idScene, name)

@router.post("/admin/removeMixerScene")
async def remove_mixer_scene(request: Request, idScene: int = Form(...)):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return admin_service.remove_mixer_scene(request, idScene)


# default user layout
@router.get("/layout")
async def default_user_layout(request: Request):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return admin_service.load_default_layout(user["sub"])

@router.post("/layout")
async def default_user_layout(request: Request, layouts: list[ChannelLayoutDTO]):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return admin_service.save_default_layout(user["sub"], layouts)

