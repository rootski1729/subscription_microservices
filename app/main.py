from fastapi import FastAPI
from app.api.routes import router
from app.core.config import settings
from app.db.session import engine, Base
from app.models import models
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.expiry_task import expire_subscriptions

Base.metadata.create_all(bind=engine)


app = FastAPI()
app.include_router(router, prefix=settings.API_V1_STR, tags=["subscriptions"])

# every 60 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(expire_subscriptions, 'interval', minutes=60)
scheduler.start()

