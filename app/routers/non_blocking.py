import asyncio
from fastapi import APIRouter
from app.services.async_service import (
    async_db_query,
    async_external_api,
    async_cpu_intensive,
    async_mixed_workflow
)

router = APIRouter(prefix="/non-blocking", tags=["non-blocking"])

@router.get("/db-query")
async def non_blocking_db_endpoint():
    return await async_db_query()

@router.get("/external-api")
async def non_blocking_external_endpoint():
    return await async_external_api()

@router.get("/cpu-intensive/{n}")
async def non_blocking_cpu_endpoint(n: int):
    result = await async_cpu_intensive(n)
    return {"result": result, "input": n}

@router.get("/mixed-workflow/{user_id}")
async def non_blocking_mixed_endpoint(user_id: int):
    return await async_mixed_workflow(user_id)

@router.get("/parallel")
async def parallel_execution_endpoint():
    tasks = [
        async_db_query(),
        async_external_api(),
        async_cpu_intensive(1)
    ]
    results = await asyncio.gather(*tasks)
    return {
        "db_result": results[0],
        "api_result": results[1],
        "cpu_result": results[2]
    }

@router.get("/concurrent-requests")
async def concurrent_endpoint():
    async def single_request(i):
        await asyncio.sleep(1)
        return {"request": i, "status": "completed"}
    
    tasks = [single_request(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    return results