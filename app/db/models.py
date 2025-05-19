from pydantic import BaseModel
from typing import Optional

class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None 