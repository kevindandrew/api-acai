from datetime import datetime
from pydantic import BaseModel


class BackupResponse(BaseModel):
    filename: str
    size_mb: float
    created_at: datetime
    message: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BackupListResponse(BaseModel):
    filename: str
    size_mb: float
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
