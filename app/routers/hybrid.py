import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.blocking_service import blocking_db_query
from app.services.async_service import async_db_query

router = APIRouter(prefix="/hybrid", tags=["hybrid"])
executor = ThreadPoolExecutor(max_workers=10)

@router.get("/thread-pool-db")
async def thread_pool_db_endpoint():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, blocking_db_query)
    return result

@router.get("/background-task")
async def background_task_endpoint():
    async def background_work():
        await asyncio.sleep(5)
        print("Background task completed")
    
    asyncio.create_task(background_work())
    return {"message": "Immediate response, task running in background"}

@router.get("/async-with-sync-deps")
async def async_with_sync(db: Session = Depends(get_db)):
    loop = asyncio.get_event_loop()
    
    async def fetch_data():
        users = await loop.run_in_executor(
            executor,
            lambda: db.query(User).all()
        )
        return [{"id": u.id, "username": u.username} for u in users]
    
    async def call_external():
        await asyncio.sleep(2)
        return {"external": "data"}
    
    users, external = await asyncio.gather(fetch_data(), call_external())
    return {"users": users, "external": external}

@router.get("/producer-consumer")
async def producer_consumer_endpoint():
    queue = asyncio.Queue()
    
    async def producer():
        for i in range(5):
            await asyncio.sleep(0.5)
            await queue.put(f"Item {i}")
        await queue.put(None)
    
    async def consumer():
        results = []
        while True:
            item = await queue.get()
            if item is None:
                break
            results.append(item)
            queue.task_done()
        return results
    
    await producer()
    return await consumer()