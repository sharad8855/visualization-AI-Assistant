from fastapi import APIRouter, HTTPException
from ..db.models import DatabaseConfig, BaseResponse
from ..db.database import save_database_config

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/database-config", response_model=BaseResponse)
async def save_database_credentials(config: DatabaseConfig):
    try:
        save_database_config(config)
        return BaseResponse(
            success=True,
            message="Database configuration saved successfully",
            data={"host": config.host, "database": config.database}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 