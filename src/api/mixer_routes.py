from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from auth.security import get_current_user, verify_mixer
from services.mixer_service import MixerService

router = APIRouter(
    prefix="/mixer",
    tags=["Mixer"]
)
mixer_service = MixerService()


#fader
@router.get("/fader")
async def fader(request: Request):
    user = get_current_user(request)
    verify_mixer(user["sub"]) 

    return mixer_service.load_fader()

@router.post("/fader")
async def set_fader(request: Request):
    user = get_current_user(request)
    token = request.cookies.get("access_token")
    verify_mixer(user["sub"])   
    
    data = await request.json()
    canaleId = data.get("canaleId")
    value = data.get("value")

    mixer_service.set_fader_value(token, canaleId,value)

@router.post("/fader/switch")
async def set_switch_channel(request : Request):
    user = get_current_user(request)
    verify_mixer(user["sub"])   
    token = request.cookies.get("access_token")

    data = await request.json()
    canaleId = data.get("canaleId")
    switch = data.get("switch")

    mixer_service.set_switch_channel(token, canaleId=canaleId, switch=switch)


@router.post("/set/main")
async def set_fader_main(request: Request):
    user_data = get_current_user(request)
    verify_mixer(user_data["sub"])
    token = request.cookies.get("access_token")
    data = await request.json()
    value = data.get("value")

    mixer_service.set_main_fader_value(token, value)

@router.post("/switch/main")
async def set_switch_main(request: Request):
    user_data = get_current_user(request)
    verify_mixer(user_data["sub"])
    token = request.cookies.get("access_token")
    data = await request.json()
    switch = data.get("switch")

    mixer_service.set_main_switch_channel(token, switch)


#dca
@router.get("/dca")
async def dca(request: Request):
    user = get_current_user(request)
    verify_mixer(user["sub"]) 

    return mixer_service.load_dca()

@router.post("/dca")
async def set_fader_DCA(request: Request):
    user_data = get_current_user(request)
    verify_mixer(user_data["sub"])
    token = request.cookies.get("access_token")

    data = await request.json()
    dca = data.get("dca_id")
    value = data.get("value")

    mixer_service.set_dca_fader_value(token, dca, value)

@router.post("/dca/switch")
async def set_switch_DCA(request: Request):
    user_data = get_current_user(request)
    verify_mixer(user_data["sub"])
    token = request.cookies.get("access_token")

    data = await request.json()
    dca = data.get("dca_id")
    switch = data.get("switch")

    mixer_service.set_dca_switch_channel(token, dca,  switch)


#aux
@router.get("/aux")
async def aux_name(request: Request):
    user = get_current_user(request)
    verify_mixer(user["sub"]) 

    return mixer_service.load_aux_names()

@router.get("/aux/{aux_id}")
async def eq_preamp_get(request: Request, aux_id : int):
    user = get_current_user(request)
    verify_mixer(user["sub"])

    return mixer_service.get_aux_parameters(aux_id)

@router.post("/aux")
async def set_fader(request: Request):
    user = get_current_user(request)
    verify_mixer(user["sub"])  
    token = request.cookies.get("access_token") 
    
    data = await request.json()
    auxId = data.get("auxId")
    canaleId = data.get("canaleId")
    value = data.get("value")

    mixer_service.set_fader_aux_value(token, auxId, canaleId, value)

@router.post("/aux/switch")
async def set_fader(request: Request):
    user = get_current_user(request)
    verify_mixer(user["sub"])   
    token = request.cookies.get("access_token")
    
    data = await request.json()
    auxId = data.get("auxId")
    canaleId = data.get("canaleId")
    value = data.get("value")

    mixer_service.set_switch_aux_value(token, auxId, canaleId, value)


#scene
@router.get("/scene")
async def fader(request: Request):
    user = get_current_user(request)
    verify_mixer(user["sub"]) 

    return mixer_service.load_scenes()


@router.get("/loadScene/{scene_id}")
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