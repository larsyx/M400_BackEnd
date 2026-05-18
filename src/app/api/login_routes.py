from fastapi import APIRouter, Form, Request
from app.services.auth_service import AuthService
from app.dao.user_dao import UserDAO


router = APIRouter()
userDAO = UserDAO()
auth_service = AuthService()


@router.post("/login")
async def login(request : Request, username: str = Form(...)):

    result = auth_service.login(username)

    return result