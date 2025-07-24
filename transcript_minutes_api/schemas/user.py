from pydantic import BaseModel

class LoginRequest(BaseModel):
    user_id: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ErrorResponse(BaseModel):
    error: dict
    
    class Config:
        schema_extra = {
            "example": {
                "error": {
                    "code": "AUTHENTICATION_FAILED",
                    "message": "Invalid credentials",
                    "details": "User ID or password is incorrect"
                }
            }
        }
