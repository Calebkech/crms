from sqlalchemy import Float, String, ForeignKey
from .base_model import BaseModel
from auth.models import db

class Transaction(BaseModel):
    __tablename__ = 'transactions'

    amount = db.Column(Float, nullable=False)
    description = db.Column(String(100), nullable=True)
    user_id = db.Column(db.String(36), ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict.update({
            'amount': self.amount,
            'description': self.description,
            'user_id': self.user_id
        })
        return obj_dict
