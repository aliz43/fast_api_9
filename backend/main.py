from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated
import uuid
from datetime import datetime, timedelta

app = FastAPI()

# --- CORS ---
origins = ["http://localhost:3000"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- Фейковые данные ---
USERS = {
    "user": {"password": "password", "role": "user"},
    "admin": {"password": "admin", "role": "admin"},
}

TOKENS = {}

# --- Модель ответа для токена ---
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

# --- Зависимость для проверки токена ---
async def token_verifier(authorization: Annotated[str, Header()]):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
        )
    token = authorization.split(" ")[1]
    user_data = TOKENS.get(token)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    if datetime.utcnow() - user_data["created_at"] > timedelta(hours=1):
        del TOKENS[token]
        raise HTTPException(status_code=401, detail="Срок действия токен истек")
    
    return user_data

# --- Эндпоинты API ---

@app.post("/api/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    username = form_data.username
    password = form_data.password

    user = USERS.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    token = str(uuid.uuid4())
    TOKENS[token] = {
        "username": username,
        "role": user["role"],
        "created_at": datetime.utcnow()
    }
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}

@app.post("/api/logout")
async def logout(authorization: Annotated[str, Header()]):
    token = authorization.replace("Bearer ", "")
    if token in TOKENS:
        del TOKENS[token]
    return {"message": "Вы вышли из системы"}

@app.get("/api/secret-data")
async def get_secret_data(user_data: Annotated[dict,Depends(token_verifier)]):
    return {
        "message": f"Привет, {user_data['username']}! Это секретные данные.",
        "role": user_data["role"]
    }

@app.get("/api/admin-data")
async def get_admin_data(user_data: Annotated[dict, Depends(token_verifier)]):
    if user_data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен: только для админа")
    return {"admin_message": "Добро пожаловать, администратор!"}