from fastapi.responses import RedirectResponse
from fastapi import HTTPException, status
from Database.database import DBSession
from app.models import User
from app.dao.user_dao import UserDAO
from ..auth.auth import create_access_token

class AuthService:
    def __init__(self):
        self.db = DBSession.get()

    def login(self, username):

        username = username.strip()

        user = self.db.query(User).filter(User.username == username).first()

        if user:
            token = create_access_token({"sub": user.username, "role": user.role.name})
            
            return token
        else:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail= "Credenziali errate"
            )