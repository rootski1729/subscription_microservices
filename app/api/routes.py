from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta

from typing import List

from sqlalchemy.orm import joinedload


from app.db.deps import get_db 
from app.schemas.schemas import *
from app.models.models import *
from app.core.config import settings
from app.core.security import create_access_token, get_current_user

router = APIRouter()

# add subscriptions
@router.post("/subscriptions", response_model = SubscriptionOut, status_code=status.HTTP_201_CREATED)
def create_subscription(subs: SubscriptionCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        plan = db.query(Plan).filter(Plan.id == subs.plan_id).first()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
        
        print(current_user)
        
        db.query(Subscription).filter(
            Subscription.user_id == current_user,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).update(
            {"status": SubscriptionStatus.EXPIRED})
        
        sub_record = Subscription(
            user_id=current_user,
            plan_id=plan.id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=plan.duration),
            status=SubscriptionStatus.ACTIVE)
        db.add(sub_record)
        db.commit()
        db.refresh(sub_record)
        return SubscriptionOut.model_validate(sub_record)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"An error occurred while creating the subscription: {str(e)}"
        )

#get subscription of user    
@router.get("/subscriptions/{user_id}", response_model= SubscriptionOut)
def get_subscription(user_id: UUID4, db: Session = Depends(get_db)):
    try:
        subscription = db.query(Subscription).options(joinedload(Subscription.plan)).filter(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()
        
        if not subscription or subscription.status != SubscriptionStatus.ACTIVE:
            raise HTTPException(status_code=404, detail = "No Active Subscription found for this user")
        
        if subscription.end_date < datetime.utcnow():
            subscription.status = SubscriptionStatus.EXPIRED
            db.commit()
            raise HTTPException(status_code=404, detail="Subscription has expired")
        
        return SubscriptionOut.model_validate(subscription)
    
    except Exception as e:
        raise HTTPException(status_code = 404, detail=f"An error occurred while fetching the subscription: {str(e)}")
    

#update subscription of user
@router.put("/subscriptions/{user_id}", response_model=SubscriptionOut)
def update_subscription(user_id: UUID4, update: SubscriptionCreate, db: Session= Depends(get_db)):
    try:
        sub = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()

        if not sub:
            raise HTTPException(status_code=404, detail="No active subscription found to update")

        plan = db.query(Plan).filter(Plan.id == update.plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="New plan not found")

        sub.plan_id = plan.id
        sub.start_date = datetime.utcnow()
        sub.end_date = datetime.utcnow() + timedelta(days=plan.duration)
        db.commit()
        db.refresh(sub)
        return SubscriptionOut.model_validate(sub)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update subscription: {str(e)}")
    

#delete subscription of user
@router.delete("/subscriptions/{user_id}")
def cancel_subscription(user_id: UUID4, db: Session = Depends(get_db)):
    try:
        sub = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()

        if not sub:
            raise HTTPException(status_code=404, detail="No active subscription to cancel")

        sub.status = SubscriptionStatus.CANCELLED
        db.commit()
        return {"detail": "Subscription cancelled"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to cancel subscription: {str(e)}")


#get list of user subscriptions history
@router.get("/subscriptions/history/{user_id}", response_model=List[SubscriptionOut])
def get_subscription_history(user_id: UUID4, db: Session = Depends(get_db)):
    try:
        return db.query(Subscription).options(joinedload(Subscription.plan)).filter(Subscription.user_id == user_id).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

#get all plans
@router.get("/plans", response_model=List[PlanOut])
def list_plans(db: Session = Depends(get_db)):
    return db.query(Plan).all()


#JWT implementaion (create token)
@router.post("/createtoken", response_model=str)
def create_token(user_id: UUID4, db: Session = Depends(get_db)):
    try:
        token = create_access_token(data={"user_id": str(user_id)})
        return token
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Failed to create token: {str(e)}")
    

#create plans
@router.post("/plans", response_model=PlanOut)
def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    plan_obj = Plan(**plan.dict())
    db.add(plan_obj)
    db.commit()
    db.refresh(plan_obj)
    return plan_obj
