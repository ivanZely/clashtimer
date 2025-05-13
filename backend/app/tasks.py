from sqlalchemy.orm import Session
from . import models

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).offset(skip).limit(limit).all()

def create_user_task(db: Session, task: models.TaskCreate, user_id: int):
    db_task = models.Task(**task.dict(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def complete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if db_task:
        db_task.completed = True
        db.commit()
        db.refresh(db_task)
    return db_task

# Agrega lógica para recompensas, experiencia, etc. aquí