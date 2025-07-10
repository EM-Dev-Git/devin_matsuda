from pydantic import BaseModel

class LoginRequest(BaseModel):
    user_id: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RegisterRequest(BaseModel):
    user_id: str
    password: str

class RegisterResponse(BaseModel):
    message: str
    user_id: str
