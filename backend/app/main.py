from fastapi import FastAPI, HTTPException, Depends
from . import models, security, tasks
from typing import List
from sqlalchemy.orm import Session
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine) # Crear la base de datos

app = FastAPI()

# Dependency para la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rutas de autenticación
@app.post("/token", response_model=security.Token)
async def login(form_data: security.OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Dependency para obtener el usuario actual
async def get_current_user(token: str = Depends(security.oauth2_scheme), db: Session = Depends(get_db)):
    user = security.get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return user

# Rutas de usuario
@app.post("/users/", response_model=models.User, tags=["Users"])
def create_user(user: models.UserCreate, db: Session = Depends(get_db)):
    db_user = security.get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    return security.create_user(db=db, user=user)

@app.get("/users/me/", response_model=models.User, tags=["Users"])
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/users/", response_model=List[models.User], tags=["Users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = security.get_users(db, skip=skip, limit=limit)
    return users

# Rutas de tareas (ejemplo)
@app.post("/tasks/", response_model=models.Task, tags=["Tasks"])
def create_task(task: models.TaskCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = tasks.create_user_task(db=db, task=task, user_id=current_user.id)
    return db_task

@app.get("/tasks/", response_model=List[models.Task], tags=["Tasks"])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks_list = tasks.get_tasks(db, skip=skip, limit=limit)
    return tasks_list


models.Base.metadata.create_all(bind=engine)  # Crear la base de datos