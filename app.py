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

@app.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")
    action = payload.get("action")

    # STEP 1: Filter important events
    IMPORTANT_EVENTS = ["push", "pull_request"]

    if event not in IMPORTANT_EVENTS:
        print(f"Ignored event: {event}")
        return {"message": "ignored"}

    # STEP 2: Extra logic for PR merge (impressive)
    if event == "pull_request":
        if action == "closed" and payload.get("pull_request", {}).get("merged"):
            print("PR Merged!")

    # STEP 3: Store in DB safely
    db = SessionLocal()
    try:
        new_event = models.WebhookEvent(
            event_type=event,
            action=action,
            data=json.dumps(payload)
        )

        db.add(new_event)
        db.commit()

        print(f"Stored event: {event}")

    except Exception as e:
        db.rollback()
        print("DB Error:", e)

    finally:
        db.close()

    return {"status": "stored"}

# Fetch stored events
@app.get("/events")
def get_events():
    db = SessionLocal()
    events = db.query(models.WebhookEvent).all()
    db.close()

    return events

@app.get("/events/{event_type}")
def get_event_by_type(event_type: str):
    db = SessionLocal()
    events = db.query(models.WebhookEvent).filter(
        models.WebhookEvent.event_type == event_type
    ).all()
    db.close()
    return events