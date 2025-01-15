from sqlalchemy import Float, String, ForeignKey, Integer
from .base_model import BaseModel
from extensions import db

class Account(BaseModel):
    __tablename__ = 'accounts'

    name = db.Column(String(100), nullable=False)
    description = db.Column(String(255), nullable=True)
    balance = db.Column(Float, default=0.0)
    account_type = db.Column(String(50), nullable=False)

    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict.update({
            'name': self.name,
            'description': self.description,
            'balance': self.balance,
            'account_type': self.account_type
        })
        return obj_dict