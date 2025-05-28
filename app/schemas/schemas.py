from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime
from app.models.models import SubscriptionStatus

class PlanCreate(BaseModel):
    name: str
    price: float
    features: List[str]
    duration: int

class PlanOut(PlanCreate):
    id: UUID4
    
    model_config = {
        "from_attributes": True 
    }

class SubscriptionCreate(BaseModel):
    plan_id: UUID4

class SubscriptionOut(BaseModel):
    id: UUID4
    user_id: UUID4
    plan: PlanOut
    status: SubscriptionStatus
    start_date: datetime
    end_date: datetime
    
    model_config = {
        "from_attributes": True  
    }
