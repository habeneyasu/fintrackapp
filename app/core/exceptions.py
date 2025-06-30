from fastapi import HTTPException, status

class ConflictError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

# Add these new exceptions
class AuthenticationError(UnauthorizedError):
    """Specific error for failed authentication"""
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(detail=detail)

class AccountLockedError(UnauthorizedError):
    """Error for inactive/locked accounts"""
    def __init__(self, detail: str = "Account is inactive"):
        super().__init__(detail=detail)

class CredentialValidationError(HTTPException):
    """Error for password/credential validation issues"""
    def __init__(self, detail: str = "Credential validation failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )