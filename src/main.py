from fastapi.exception_handlers import http_exception_handler
from Database.database import DBSession
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api import admin_routes, login_routes, mixer_routes, user_routes, video_routes
from api import ws_routes
from fastapi.staticfiles import StaticFiles
import os
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from midi.exceptions import MidiConnectionError


templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "view", "static"))

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(admin_routes.router)
app.include_router(login_routes.router)
app.include_router(ws_routes.router)
app.include_router(user_routes.router)
app.include_router(mixer_routes.router)
app.include_router(video_routes.router)

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "view", "static")), name="static")


@app.exception_handler(MidiConnectionError)
async def midi_connection_error_handler(request: Request, exc: MidiConnectionError):
    try:
        await ws_routes.ws_service.broadcast_midi_error(exc.message, exc.code)
    except Exception as e:
        print(f"[midi handler] broadcast fallito: {e}")
    return JSONResponse(
        status_code=503,
        content={"code": exc.code, "message": exc.message},
    )


@app.on_event("shutdown")
def shutdown_event():
    DBSession.close()

