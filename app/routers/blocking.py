import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.task import Task
from app.services.blocking_service import (
    blocking_db_query,
    blocking_external_api,
    blocking_cpu_intensive,
    blocking_mixed_workflow
)

router = APIRouter(prefix="/blocking", tags=["blocking"])

@router.get("/db-query")
def blocking_db_endpoint():
    return blocking_db_query()

@router.get("/external-api")
def blocking_external_endpoint():
    return blocking_external_api()

@router.get("/cpu-intensive/{n}")
def blocking_cpu_endpoint(n: int):
    return {"result": blocking_cpu_intensive(n), "input": n}

@router.get("/mixed-workflow/{user_id}")
def blocking_mixed_endpoint(user_id: int):
    return blocking_mixed_workflow(user_id)

@router.get("/chain-blocking")
def chain_blocking_endpoint():
    time.sleep(2)
    users = blocking_db_query()
    time.sleep(2)
    external = blocking_external_api()
    time.sleep(2)
    return {"users": users, "external": external}

@router.get("/query-sync")
def query_sync(db: Session = Depends(get_db)):
    time.sleep(3)
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "email": u.email} for u in users]