from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from app.auth.security import get_current_user, verify_admin
from app.services.admin_service import AdminService
from app.services.scene_service import SceneService 
router = APIRouter()


scene_service = SceneService()

import os

admin_service = AdminService()

@router.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    user = get_current_user(request)
    verify_admin(user["sub"])

    index_path = os.path.join(os.path.dirname(__file__), ".." ,"view", "administration", "home.html")  
    return FileResponse(index_path)

# user manage
@router.get("/admin/manageUser", response_class=HTMLResponse)
async def manage_user(request: Request):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return admin_service.load_manage_user(request, user["sub"])


@router.post("/admin/createUser")
async def create_user(request: Request, username: str = Form(...), nome: str = Form(...), ruolo: str = Form(...)):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return admin_service.create_user(request, user["sub"], username, nome, ruolo)


@router.post("/admin/deleteUser", response_class=HTMLResponse)
async def delete_user(request : Request, username: str = Form(...)):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return admin_service.delete_user(request, user["sub"], username)



#scene manage   
@router.get("/admin/manageScene", response_class=HTMLResponse)
async def manage_scene(request: Request):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return scene_service.manage_scene(request, user["sub"])

@router.post("/admin/create_scene")
async def create_scene(request : Request, nome: str = Form(...), descrizione:str = Form(...)):
    user = get_current_user(request)
    verify_admin(user["sub"])
    return scene_service.create_scene(request, user["sub"], nome, descrizione)


@router.get("/admin/scene_{scene_id}/")
async def get_scene(request : Request, scene_id: int):
    user = get_current_user(request)
    verify_admin(user["sub"])
    
    return scene_service.get_scene(request, user["sub"], scene_id)

@router.post("/admin/scene_{scene_id}/deleteScene", response_class=HTMLResponse)
async def add_partecipanti_scena(request : Request, scene_id : int):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return scene_service.delete_scene(request, user["sub"], scene_id)

#manage user scene
@router.post("/admin/scene_{scene_id}/addParticipants")
async def add_participants_scene(request : Request, scene_id : int, username : str = Form(...), aux : str = Form(...)):
    user = get_current_user(request)
    verify_admin(user["sub"])
    
    return scene_service.add_partecipante(request, user["sub"], scene_id, username, aux)

@router.delete("/admin/scene_{scene_id}/removeParticipants", response_class=HTMLResponse)
async def remove_participants_scene(request : Request, scene_id : int, username : str = Form(...)):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return scene_service.remove_partecipante(request, user["sub"], scene_id, username)

@router.post("/admin/scene_{scene_id}/changeAux")
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
@router.get("/admin/defaultUserLayout", response_class=HTMLResponse)
async def default_user_layout(request: Request):
    user = get_current_user(request)
    verify_admin(user["sub"])

    return admin_service.load_default_user_layout(request)

@router.post("/admin/set/defaultUserLayout")
async def default_user_layout(request: Request):
    user = get_current_user(request)
    verify_admin(user["sub"])

    data = await request.json()
    channels = data.get("channels", [])
    drums = data.get("drums", [])


    return admin_service.save_default_user_layout(channels, drums)