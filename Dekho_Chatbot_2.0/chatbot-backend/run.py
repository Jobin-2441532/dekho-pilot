"""
Production server entrypoint — 4 async workers with uvloop for 50-100 concurrent users.
Run: python run.py
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        workers=4,
        loop="asyncio",       # use "uvloop" if uvloop is installed
        log_level="info",
        access_log=True,
        timeout_keep_alive=30,
        limit_concurrency=200, # max concurrent connections
        backlog=512,
    )
