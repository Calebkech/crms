from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, DateTime
from datetime import datetime
import uuid
cash_flow_db = SQLAlchemy

class BaseModel(cash_flow_db.Model):
    __abstract__ = True

    id = Column(uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)