from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from auth.security import get_current_user, verify_mixer
from services.aux_service import AuxService
from services.mixer_service import MixerService

router = APIRouter(
    prefix="/mixer",
    tags=["Mixer"]
)
mixer_service = MixerService()
aux_service = AuxService()


@router.get("/home")
async def load_home(request: Request):
    user = get_current_user(request)
    verify_mixer(user["sub"])

    return mixer_service.load_home()

#fader
@router.get("/fader")
async def fader(request: Request):
    user = get_current_user(request)
    verify_mixer(user["sub"]) 

    return mixer_service.load_fader()


#dca
@router.get("/dca")
async def dca(request: Request):
    user = get_current_user(request)
    verify_mixer(user["sub"]) 

    return mixer_service.load_dca()


#aux
@router.get("/aux")
async def aux_name(request: Request):
    user = get_current_user(request)
    verify_mixer(user["sub"]) 

    return aux_service.load_aux_names()

@router.get("/aux/{aux_id}")
async def eq_preamp_get(request: Request, aux_id : int):
    user = get_current_user(request)
    verify_mixer(user["sub"])

    return mixer_service.get_aux_parameters(aux_id)

#scene
@router.get("/scene")
async def fader(request: Request):
    user = get_current_user(request)
    verify_mixer(user["sub"]) 

    return mixer_service.load_scenes()


@router.post("/scene/{scene_id}")
async def load_scene(request: Request, scene_id: int):
    user = get_current_user(request)
    verify_mixer(user["sub"])   

    return mixer_service.load_scene(scene_id)


#Eq
@router.post("/EQ")
async def eq_set(request: Request):
    user = get_current_user(request)
    verify_mixer(user["sub"])
    token = request.cookies.get("access_token")

    data = await request.json()
    channel = data.get("channel")
    typeFreq = data.get("typeFreq")
    typeEq = data.get("typeEq")
    value = data.get("value")


    mixer_service.eq_set(token, channel, typeFreq, typeEq, value)

@router.get("/EQ/{channel}")
async def eq_get(request: Request, channel : int):
    user = get_current_user(request)
    verify_mixer(user["sub"])
    

    return mixer_service.eq_get(channel)


@router.post("/EQ/Switch")
async def eq_switch_set(request: Request):
    user = get_current_user(request)
    verify_mixer(user["sub"])
    token = request.cookies.get("access_token")
    data = await request.json()
    channel = data.get("channel")
    switch = data.get("switch")

    mixer_service.eq_switch_set(token, channel, switch)

@router.get("/EQ/Switch/{channel}")
async def eq_switch_get(request: Request, channel: int):
    user = get_current_user(request)
    verify_mixer(user["sub"])

    return mixer_service.eq_switch_get(channel)

@router.post("/Preamp")
async def eq_preamp_set(request: Request):
    user = get_current_user(request)
    verify_mixer(user["sub"])
    token = request.cookies.get("access_token")

    data = await request.json()
    channel = data.get("channel")
    value = data.get("value")

    mixer_service.eq_preamp_set(token, channel, int(value))

@router.get("/Preamp/{channel}")
async def eq_preamp_get(request: Request, channel : int):
    user = get_current_user(request)
    verify_mixer(user["sub"])

    return mixer_service.eq_preamp_get(channel)


#Disposizione
@router.post("/saveDisposition")
async def save_disposition(request: Request):
    user = get_current_user(request)
    verify_mixer(user["sub"])

    data = await request.json()
    disposition = data.get("disposition")

    mixer_service.save_disposition(disposition)