from fastapi import FastAPI, Request
from database import SessionLocal, engine
import models
import json

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Webhook server running"}

# Webhook endpoint
@app.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")
    action = payload.get("action")

    db = SessionLocal()

    new_event = models.WebhookEvent(
        event_type=event,
        action=action,
        data=json.dumps(payload)
    )

    db.add(new_event)
    db.commit()
    db.close()

    print(f"Stored event: {event}")

    return {"status": "stored"}

# Fetch stored events
@app.get("/events")
def get_events():
    db = SessionLocal()
    events = db.query(models.WebhookEvent).all()
    db.close()

    return events