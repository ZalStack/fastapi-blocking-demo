import asyncio
import time
import httpx

BASE_URL = "http://localhost:8000"

async def load_test_blocking():
    print("=" * 50)
    print("LOAD TEST: BLOCKING ENDPOINTS")
    print("=" * 50)
    
    async def make_request(client, i):
        start = time.time()
        try:
            response = await client.get(f"{BASE_URL}/blocking/db-query", timeout=5.0)
            elapsed = time.time() - start
            return f"Request {i}: {response.status_code} ({elapsed:.2f}s)"
        except Exception as e:
            elapsed = time.time() - start
            return f"Request {i}: ERROR ({elapsed:.2f}s) - {e}"
    
    async with httpx.AsyncClient() as client:
        tasks = [make_request(client, i) for i in range(10)]
        start = time.time()
        results = await asyncio.gather(*tasks)
        total = time.time() - start
    
    for result in results:
        print(result)
    print(f"\nTotal time for 10 concurrent requests: {total:.2f}s")
    print(f"Expected serial time: ~20s (10 requests * 2s each)")
    print()

async def load_test_non_blocking():
    print("=" * 50)
    print("LOAD TEST: NON-BLOCKING ENDPOINTS")
    print("=" * 50)
    
    async def make_request(client, i):
        start = time.time()
        try:
            response = await client.get(f"{BASE_URL}/non-blocking/db-query", timeout=5.0)
            elapsed = time.time() - start
            return f"Request {i}: {response.status_code} ({elapsed:.2f}s)"
        except Exception as e:
            elapsed = time.time() - start
            return f"Request {i}: ERROR ({elapsed:.2f}s) - {e}"
    
    async with httpx.AsyncClient() as client:
        tasks = [make_request(client, i) for i in range(10)]
        start = time.time()
        results = await asyncio.gather(*tasks)
        total = time.time() - start
    
    for result in results:
        print(result)
    print(f"\nTotal time for 10 concurrent requests: {total:.2f}s")
    print(f"Expected concurrent time: ~2s (non-blocking)")
    print()

async def demonstrate_blocking_impact():
    print("=" * 50)
    print("DEMO: EVENT LOOP BLOCKING IMPACT")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        print("Sending 1 slow request (5s blocking)...")
        slow_task = client.get(f"{BASE_URL}/blocking/db-query")
        
        await asyncio.sleep(0.5)
        
        print("Sending 5 fast requests (should be instant but blocked)...")
        fast_tasks = [client.get(f"{BASE_URL}/health") for _ in range(5)]
        
        start = time.time()
        all_results = await asyncio.gather(slow_task, *fast_tasks)
        total = time.time() - start
        
        print(f"Health check responses time: {total:.2f}s")
        print("Fast requests were blocked by the slow request!")
    print()

async def main():
    await demonstrate_blocking_impact()
    await load_test_blocking()
    await load_test_non_blocking()

if __name__ == "__main__":
    asyncio.run(main())