from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=4000)
    top_k: Optional[int] = Field(default=None, ge=1, le=20)


class SourceItem(BaseModel):
    page: int
    score: float
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[SourceItem]


class UploadResponse(BaseModel):
    job_id: str
    status: str
    message: str


class LocalIndexRequest(BaseModel):
    pdf_path: str = Field(..., min_length=3)
    force: bool = False


class JobStatus(BaseModel):
    job_id: str
    status: str
    detail: str
