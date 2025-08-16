from pydantic import BaseModel

class LoginIn(BaseModel):
    user_id: str
    user_pwd: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
