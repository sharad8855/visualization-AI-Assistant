from fastapi import APIRouter, HTTPException
from app.db.models import (
    DatabaseConfig, BaseResponse, TablesResponse, 
    TableData, VisualizationResponse, QueryRequest
)
from app.db.mysql import MySQLConnector
from app.services.gemini_service import GeminiService
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
db = MySQLConnector()
gemini = GeminiService()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/database-config", response_model=BaseResponse)
async def save_database_credentials(config: DatabaseConfig):
    try:
        # Save the configuration
        with open("app/config/database.json", "w") as f:
            f.write(config.json())
        return BaseResponse(
            success=True,
            message="Database configuration saved successfully",
            data={"host": config.host, "database": config.database}
        )
    except Exception as e:
        logger.error(f"Error saving database config: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/tables", response_model=TablesResponse)
async def get_tables():
    try:
        # Get all tables with their structure
        tables = db.get_all_tables()
        
        if not tables:
            return TablesResponse(
                success=False,
                message="No tables found or error occurred",
                tables={},
                error="Database error or no tables exist"
            )
            
        # Update Gemini service with database structure
        gemini.set_database_structure(tables)
        
        # Log the database structure for debugging
        logger.info(f"Database structure: {json.dumps(tables, indent=2)}")
            
        return TablesResponse(
            success=True,
            message="Tables retrieved successfully",
            tables=tables
        )
        
    except Exception as e:
        logger.error(f"Error in get_tables endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    finally:
        db.disconnect()

@router.post("/visualize", response_model=VisualizationResponse)
async def visualize_data(request: QueryRequest):
    try:
        # Get current database structure
        tables = db.get_all_tables()
        if not tables:
            raise HTTPException(
                status_code=404,
                detail="No tables found in database"
            )
        
        # Update Gemini service with database structure
        gemini.set_database_structure(tables)
        
        # Convert natural language query to SQL
        sql_query = gemini.convert_to_sql(request.query)
        logger.info(f"Generated SQL query: {sql_query}")
        
        # Execute the query
        results, total_count = db.execute_query(sql_query)
        
        # Format the results using Gemini
        visualization_data = gemini.format_visualization(request.query, {
            "results": results,
            "total_count": total_count
        })
        
        return visualization_data
        
    except Exception as e:
        logger.error(f"Error in visualization endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    finally:
        db.disconnect()        