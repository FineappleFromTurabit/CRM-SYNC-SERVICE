# app/models/hubspot.py
from pydantic import BaseModel
from typing import Dict, Any


class HubSpotContact(BaseModel):
    properties: Dict[str, Any]

    @staticmethod
    def from_internal(customer):
        return HubSpotContact(
            properties={
                "email": customer.email,
                "firstname": customer.name,
                "company": customer.company or "",
            }
        )


class HubSpotTicket(BaseModel):
    properties: Dict[str, Any]

    @staticmethod
    def from_internal(ticket):
        return HubSpotTicket(
            properties={
                "subject": ticket.title,
                "content": ticket.description or "",
                "Priority": ticket.priority.lower(),
                "hs_pipeline_stage": ticket.status.lower(),
            }
        )
