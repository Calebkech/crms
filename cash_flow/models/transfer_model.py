from sqlalchemy import Float, String
from .base_model import BaseModel
from extensions import db

class Transfer(BaseModel):
    __tablename__ = 'transfers'

    from_account_id = db.Column(String(36), db.ForeignKey('accounts.id'), nullable=False)  # Account transferring from
    to_account_id = db.Column(String(36), db.ForeignKey('accounts.id'), nullable=False)  # Account transferring to
    amount = db.Column(Float, nullable=False)  # Transfer amount
    description = db.Column(String(255), nullable=True)  # Optional transfer description

    from_account = db.relationship('Account', foreign_keys=[from_account_id], backref='outgoing_transfers')
    to_account = db.relationship('Account', foreign_keys=[to_account_id], backref='incoming_transfers')

    def to_dict(self):
        """Convert the Transfer object to a dictionary for easy serialization."""
        obj_dict = super().to_dict()  # Get fields from BaseModel
        obj_dict.update({
            'from_account_id': self.from_account_id,
            'to_account_id': self.to_account_id,
            'amount': self.amount,
            'description': self.description,
        })
        return obj_dict
