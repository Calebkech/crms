from sqlalchemy import Integer, String 
from .base_model import BaseModel
from extensions import db

class CustomerContact(BaseModel):
    __tablename__ = 'customer_contacts'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    contact_type = db.Column(String(50), nullable=False)  # e.g., 'email', 'phone'
    contact_value = db.Column(String(255), nullable=False)  # e.g., 'example@domain.com', '123-456-7890'

    customer = db.relationship('Customer', backref=db.backref('contacts', lazy=True))

    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict.update({
            'customer_id': self.customer_id,
            'contact_type': self.contact_type,
            'contact_value': self.contact_value,
        })
        return obj_dict

