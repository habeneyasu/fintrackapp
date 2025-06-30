# In app/core/decorators.py
from functools import wraps
from fastapi import HTTPException
from .exceptions import ConflictError, NotFoundError

def handle_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ConflictError as e:
            raise e  # Already properly formatted
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )
    return wrapper