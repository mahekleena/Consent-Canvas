# backend/models.py
from pydantic import BaseModel
from typing import Dict, Optional

class ConsentRequest(BaseModel):
    domain: str
    banner_text: str
    user_preferences: Optional[Dict[str, bool]] = None  # e.g. {"ads": false, "analytics": true}

class ConsentResponse(BaseModel):
    decision: str  # "Accept All" | "Reject All" | "Custom"
    custom_preferences: Optional[Dict[str, bool]] = None
    model_labels: Optional[Dict[str, float]] = None  # confidence per purpose
