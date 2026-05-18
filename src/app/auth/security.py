
from fastapi import  HTTPException, Request, status, WebSocket
from app.dao.user_dao import UserDAO
from app.auth.auth import verify_token  

userDAO = UserDAO()

# Funzione che estrae l'utente corrente a partire dal token
def get_current_user(request : Request):
    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante nei cookie")

    
    payload = verify_token(token.split(" ")[1])  # Verifica il token
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token non valido")
    elif userDAO.get_user_by_username(payload["sub"]) == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token non valido")

    return payload

def get_current_user_token(access_token):
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mancante nei cookie")

    payload = verify_token(access_token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token non valido")
    elif userDAO.get_user_by_username(payload["sub"]) == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token non valido")

    return payload

def verify_admin(user):
    if not userDAO.is_admin(user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="non sei autorizzato")
    return True

def verify_mixer(user):
    if not userDAO.is_mixer(user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="non sei autorizzato")
    return True

def verify_video(user):
    if not userDAO.is_video(user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="non sei autorizzato")
    return True