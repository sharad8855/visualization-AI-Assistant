from pydantic import BaseModel
from typing import Optional

class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class DatabaseConfig(BaseModel):
    host: str
    user: str
    password: str
    database: str 