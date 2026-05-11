import asyncio
import aiohttp
from app.database import get_async_pool

async def async_db_query():
    await asyncio.sleep(2)
    pool = await get_async_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id, username, email FROM users")
            result = await cur.fetchall()
            return [{"id": r[0], "username": r[1], "email": r[2]} for r in result]

async def async_external_api():
    async with aiohttp.ClientSession() as session:
        await asyncio.sleep(3)
        async with session.get("https://jsonplaceholder.typicode.com/posts/1") as response:
            return await response.json()

async def async_cpu_intensive(n):
    result = 0
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: sum(range(n * 1000000)))
    return result

async def async_mixed_workflow(user_id):
    pool = await get_async_pool()
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await asyncio.sleep(1)
            await cur.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
            user = await cur.fetchone()
            
            await asyncio.sleep(1)
            await cur.execute("SELECT id, title, status FROM tasks WHERE user_id = %s", (user_id,))
            tasks = await cur.fetchall()
    
    async with aiohttp.ClientSession() as session:
        await asyncio.sleep(1)
        async with session.get(f"https://jsonplaceholder.typicode.com/users/{user_id}") as response:
            external = await response.json()
    
    return {
        "user": {"id": user[0], "username": user[1]} if user else None,
        "tasks": [{"id": t[0], "title": t[1], "status": t[2]} for t in tasks],
        "external": external
    }