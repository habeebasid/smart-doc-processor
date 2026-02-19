from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# Request schemas (what users send to API)
class DocumentUploadResponse(BaseModel):
    """Response after uploading a document"""

    id: int
    filename: str
    file_size: int
    message: str


class QueryRequest(BaseModel):
    """Request to query documents"""

    question: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)  # how many chunks to retrieve


class QueryResponse(BaseModel):
    """Response to a query"""

    answer: str
    sources: List[dict]  # which chunks were used


# Response schemas (what API returns)
class DocumentOut(BaseModel):
    """Document information"""

    id: int
    filename: str
    file_type: Optional[str]
    file_size: int
    upload_date: datetime
    processed: bool

    class Config:
        from_attributes = True  # allows SQLAlchemy model conversion
