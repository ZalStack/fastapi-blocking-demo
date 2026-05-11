import time
import requests
from app.database import SessionLocal
from app.models.user import User
from app.models.task import Task

def blocking_db_query():
    db = SessionLocal()
    try:
        time.sleep(2)
        users = db.query(User).all()
        return [{"id": u.id, "username": u.username, "email": u.email} for u in users]
    finally:
        db.close()

def blocking_external_api():
    time.sleep(3)
    response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
    return response.json()

def blocking_cpu_intensive(n):
    result = 0
    for i in range(n * 1000000):
        result += i
    return result

def blocking_mixed_workflow(user_id):
    db = SessionLocal()
    try:
        time.sleep(1)
        user = db.query(User).filter(User.id == user_id).first()
        time.sleep(1)
        tasks = db.query(Task).filter(Task.user_id == user_id).all()
        time.sleep(1)
        response = requests.get(f"https://jsonplaceholder.typicode.com/users/{user_id}")
        
        return {
            "user": {"id": user.id, "username": user.username} if user else None,
            "tasks": [{"id": t.id, "title": t.title, "status": t.status} for t in tasks],
            "external": response.json()
        }
    finally:
        db.close()