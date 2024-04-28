import os
import uvicorn

host: str = os.getenv("HOST", "0.0.0.0")
port: int = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    uvicorn.run("app:app", host=host, port=port, log_level="info")