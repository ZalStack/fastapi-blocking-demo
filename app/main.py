from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from app.routers import blocking, non_blocking, hybrid

app = FastAPI(
    title="Event Loop Blocking Demo",
    description="Demonstrasi masalah Event Loop Blocking di FastAPI dan solusinya",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.middleware("http")
async def detect_blocking(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    if duration > 2.0:
        print(f"WARNING: Request {request.url} took {duration:.2f}s - possible blocking!")
    return response

app.include_router(blocking.router)
app.include_router(non_blocking.router)
app.include_router(hybrid.router)

@app.get("/")
async def root():
    return {
        "message": "Event Loop Blocking Demo API",
        "endpoints": {
            "blocking": "/blocking/*",
            "non_blocking": "/non-blocking/*",
            "hybrid": "/hybrid/*"
        },
        "warning": "Gunakan endpoint /blocking/* untuk melihat masalah blocking",
        "solution": "Gunakan endpoint /non-blocking/* untuk melihat solusi async"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "path": str(request.url)}
    )