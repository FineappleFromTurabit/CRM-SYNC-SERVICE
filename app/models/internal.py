# app/models/internal.py
from pydantic import BaseModel
from typing import Optional


class InternalCustomer(BaseModel):
    id: int
    name: str
    email: str
    company: Optional[str] = None
    # created_at: str   # ← NOT datetime

class InternalTicket(BaseModel):
    id: int
    customer_id: int
    title: str
    description: Optional[str] = None 
    priority: str
    status: str
    assigned_to: Optional[int] = None


class CreateTicketDirectRequest(BaseModel):
    customer_id: int
    title: str
    description: Optional[str] = ""
    priority: str
    assigned_to: Optional[int] = None