from sqlalchemy import Float, String, ForeignKey
from .base_model import BaseModel
from extensions import db

class Transaction(BaseModel):
    __tablename__ = 'transactions'

    name = db.Column(Float, nullable=False)
    description = db.Column(String(100), nullable=True)
    user_id = db.Column(db.String(36), ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.String(36), ForeignKey('accounts.id'), nullable=False)
    transaction_type = db.Column(String(50), nullable=False)  # e.g., 'income', 'expense', 'transfer'

    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict.update({
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'account_id': self.account_id,
            'transaction_type': self.transaction_type
        })
        return obj_dict
