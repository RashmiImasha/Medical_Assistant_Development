from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DocumentUploadResponse(BaseModel):

    id:str
    filename:str
    status: str
    message: str

class DocumentResponse(BaseModel):

    """Returned by GET endpoints — mirrors the Document DB model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    pinecone_namespace: str
    status: str
    uploaded_at: datetime
