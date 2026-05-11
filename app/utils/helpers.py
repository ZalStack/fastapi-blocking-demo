import time
from functools import wraps
from fastapi import HTTPException

def measure_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start
        return {"data": result, "execution_time": f"{elapsed:.2f}s"}
    return wrapper

def simulate_error(probability=0.3):
    import random
    if random.random() < probability:
        raise HTTPException(status_code=500, detail="Simulated internal error")