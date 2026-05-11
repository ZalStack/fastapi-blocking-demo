import asyncio
import time
import httpx

BASE_URL = "http://localhost:8000"

async def test_blocking_endpoint():
    print("Testing BLOCKING endpoint...")
    start = time.time()
    
    async with httpx.AsyncClient() as client:
        tasks = [client.get(f"{BASE_URL}/blocking/db-query") for _ in range(5)]
        results = await asyncio.gather(*tasks)
    
    total = time.time() - start
    print(f"Blocking: 5 requests took {total:.2f}s")
    print(f"Expected: ~10s if serial, Actual: {total:.2f}s\n")

async def test_non_blocking_endpoint():
    print("Testing NON-BLOCKING endpoint...")
    start = time.time()
    
    async with httpx.AsyncClient() as client:
        tasks = [client.get(f"{BASE_URL}/non-blocking/db-query") for _ in range(5)]
        results = await asyncio.gather(*tasks)
    
    total = time.time() - start
    print(f"Non-Blocking: 5 requests took {total:.2f}s")
    print(f"Expected: ~2s if parallel, Actual: {total:.2f}s\n")

async def test_parallel_execution():
    print("Testing PARALLEL execution...")
    start = time.time()
    
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get(f"{BASE_URL}/non-blocking/db-query"),
            client.get(f"{BASE_URL}/non-blocking/external-api"),
            client.get(f"{BASE_URL}/non-blocking/cpu-intensive/1"),
        ]
        results = await asyncio.gather(*tasks)
    
    total = time.time() - start
    print(f"Parallel: 3 different tasks took {total:.2f}s")
    print(f"Individual tasks run concurrently\n")

async def main():
    await test_blocking_endpoint()
    await asyncio.sleep(1)
    await test_non_blocking_endpoint()
    await asyncio.sleep(1)
    await test_parallel_execution()

if __name__ == "__main__":
    asyncio.run(main())