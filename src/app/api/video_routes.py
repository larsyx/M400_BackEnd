
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from app.dao.channel_dao import ChannelDAO
from app.dao.layout_canale_dao import LayoutCanaleDAO
from app.auth.security import get_current_user, verify_video
from app.services.video_service import VideoService

router = APIRouter()

video_service = VideoService()


@router.get("/video/home")
async def load_scene(request: Request):
    user_data = get_current_user(request)
    verify_video(user_data["sub"])

    return video_service.load_scene(request)

@router.post("/video/set")
async def set_fader(request: Request):
    user_data = get_current_user(request)
    verify_video(user_data["sub"])
    token = request.cookies.get("access_token")

    data = await request.json()
    canaleId = data.get("canaleId")
    value = data.get("value")

    video_service.set_fader(token, canaleId, value)
    

@router.post("/video/set/main")
async def set_fader_main(request: Request):
    user_data = get_current_user(request)
    verify_video(user_data["sub"])
    token = request.cookies.get("access_token")

    data = await request.json()
    value = data.get("value")
    
    video_service.set_fader_main(token, value)
   
@router.post("/video/switch/main")
async def set_switch_main(request: Request):
    user_data = get_current_user(request)
    verify_video(user_data["sub"])
    token = request.cookies.get("access_token")

    data = await request.json()
    value = data.get("switch")
    
    video_service.set_switch_main(token, value)


@router.get("/video/getFadersValue")
async def get_fader_value(request: Request):
    user_data = get_current_user(request)
    verify_video(user_data["sub"])

    return video_service.get_faders_value()