# 📦 Subscription Microservice - FastAPI

This microservice handles **subscription and plan management** using FastAPI, PostgreSQL, and Redis. It includes user authentication, subscription lifecycle, auto-expiry, and real-time event publishing via Redis.

---

## 🚀 Tech Stack

* **Backend:** FastAPI
* **Database:** PostgreSQL
* **Message Queue:** Redis (used for broadcasting expiry events)
* **ORM:** SQLAlchemy
* **Scheduler:** APScheduler
* **Auth:** JWT tokens (token must contain `sub` = user\_id)

---

## 📁 Folder Structure

```
subscription_service/
├── app/
│   ├── api/               # Route handlers
│   ├── core/              # Security and settings
│   ├── db/                # DB session
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic models
│   ├── services/          # Background expiry logic
│   └── main.py            # Entry point
├── .env                   # Environment config
├── requirements.txt       # Dependencies
```

---

## 🔐 Authentication

All subscription endpoints are protected by JWT.
You must generate a token manually (or expose a testing `/token` endpoint).

The token payload should include:

```json
{
  "sub": "<user_id>"
}
```

Use it in requests as:

```
Authorization: Bearer <token>
```

---

## 🔧 Setup Instructions

### 1. Create `.env` file

```
DATABASE_URL=postgresql://<user>:<pass>@localhost:5432/subscription_db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REDIS_URL=redis://localhost:6379
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
uvicorn app.main:app --reload
```

Access Swagger docs at:

```
http://127.0.0.1:8000/docs
```

---

## 🧪 API Endpoints

### 📝 Plans

* `POST /plans` — Create a subscription plan
* `GET /plans` — List all available plans

### 💳 Subscriptions

* `POST /subscriptions` — Subscribe to a plan (requires JWT)
* `GET /subscriptions/{user_id}` — Get user's current subscription
* `PUT /subscriptions/{user_id}` — Update subscription to a new plan
* `DELETE /subscriptions/{user_id}` — Cancel subscription (status becomes CANCELLED)
* `GET /subscriptions/history/{user_id}` — Full history of user's subscriptions

---

## ⏰ Background Expiry with Redis

### 📌 What it does:

* Checks every 60 minutes for expired subscriptions (based on `end_date`)
* Marks them as `EXPIRED`
* Publishes an event to Redis channel: `subscriptions`

### 🔁 Example Redis Message:

```
Subscription expired: <subscription_id>
```

You can subscribe to this channel using a Redis client to trigger downstream actions (e.g. email, audit logging).

---

## ⚠️ Edge Cases Handled

* Subscriptions auto-expire based on time
* Cancelled subscriptions can no longer be updated
* All DB operations are in try-catch with rollback
* Redis failure won’t block DB changes

---

## 📌 Notes

* There is **no foreign key to User** to ensure microservice isolation
* The `user_id` is passed via JWT token (`sub` claim)
* Redis is optional but used here for real-time integration potential

---

## ✅ Example Token Generation (For Local Testing)

You can temporarily add this route:

```python
@router.post("/token")
def generate_token(user_id: str = Form(...)):
    return {"access_token": create_access_token({"sub": user_id})}
```

---
