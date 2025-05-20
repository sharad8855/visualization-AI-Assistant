from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class DatabaseConfig(BaseModel):
    host: str
    user: str
    password: str
    database: str

class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None
    error: Optional[str] = None

class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool
    key: str
    default: Optional[Any] = None

class Table(BaseModel):
    name: str
    columns: List[ColumnInfo]
    first_row: Dict[str, Any]

class TableData(BaseModel):
    column_name: List[str]
    sample_data: Dict[str, Any]

class TablesResponse(BaseResponse):
    tables: Dict[str, TableData] = {}

# Visualization Models
class ChartData(BaseModel):
    title: str
    type: str
    labels: List[str]
    values: List[Any]

class VisualizationMetadata(BaseModel):
    total_records: int
    charts: Dict[str, ChartData]

class VisualizationResponse(BaseResponse):
    metadata: Optional[VisualizationMetadata] = None
    data: Optional[List[Dict[str, Any]]] = None

class QueryRequest(BaseModel):
    query: str 