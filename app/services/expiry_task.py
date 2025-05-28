from app.db.session import SessionLocal
from app.models.models import Subscription, SubscriptionStatus
from datetime import datetime
from redis import Redis
from app.core.config import settings

r = Redis.from_url(settings.REDIS_URL)

def expire_subscriptions():
    db = SessionLocal()
    try:
        expired = db.query(Subscription).filter(
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.end_date < datetime.utcnow()
        ).all()

        for sub in expired:
            sub.status = SubscriptionStatus.EXPIRED
            db.add(sub)
            r.publish("subscriptions", f"Subscription expired: {sub.id}")

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error expiring subscriptions: {e}")
    finally:
        db.close()
