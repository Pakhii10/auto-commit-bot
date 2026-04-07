from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String)
    action = Column(String, nullable=True)
    data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)