# run.py
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host=settings.DB_HOST,  # e.g. "0.0.0.0"
        port=8000,  # e.g. 8000
        reload=True,   # Auto-reload in development
        workers=1,        # Single worker (adjust if needed)
        log_level="info",
        access_log=settings.APP_DEBUG 
    )

 