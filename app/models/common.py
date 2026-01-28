# app/models/common.py
from pydantic import BaseModel
from typing import Optional


class SyncResult(BaseModel):
    internal_id: int
    crm_id: str
    action: str  # CREATED / UPDATED
    status: str  # SUCCESS / FAILED
    message: Optional[str] = None
