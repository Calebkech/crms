from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from extensions import db

class BaseModel(db.Model):
    __abstract__ = True  # This class is meant to be inherited by other models, not instantiated directly

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'created_at' in kwargs:
            self.created_at = datetime.strptime(kwargs['created_at'], '%Y-%m-%dT%H:%M:%S.%f')
        else:
            self.created_at = datetime.utcnow()
        if 'updated_at' in kwargs:
            self.updated_at = datetime.strptime(kwargs['updated_at'], '%Y-%m-%dT%H:%M:%S.%f')
        else:
            self.updated_at = datetime.utcnow()

    def to_dict(self):
        obj_dict = self.__dict__.copy()
        obj_dict['created_at'] = self.created_at.isoformat()
        obj_dict['updated_at'] = self.updated_at.isoformat()
        obj_dict['__class__'] = self.__class__.__name__
        if '_sa_instance_state' in obj_dict:
            del obj_dict['_sa_instance_state']
        return obj_dict

    def save(self, session):
        """Save the object to the database."""
        self.updated_at = datetime.utcnow()
        session.add(self)
        session.commit()

    def delete(self, session):
        """Delete the object from the database."""
        session.delete(self)
        session.commit()

    def __str__(self):
        return f"[{self.__class__.__name__}] ({self.id}) {self.to_dict()}"
