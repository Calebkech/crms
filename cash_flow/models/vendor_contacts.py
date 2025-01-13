from sqlalchemy import Integer, String 
from .base_model import BaseModel
from extensions import db

class VendorContact(BaseModel):
    __tablename__ = 'vendor_contacts'

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.String(36), db.ForeignKey('vendors.id'), nullable=False)
    contact_type = db.Column(String(50), nullable=False)  # e.g., 'email', 'phone'
    contact_value = db.Column(String(255), nullable=False)  # e.g., 'example@domain.com', '123-456-7890'

    vendor = db.relationship('Vendor', backref=db.backref('contacts', lazy=True))

    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict.update({
            'vendor_id': self.vendor_id,
            'contact_type': self.contact_type,
            'contact_value': self.contact_value,
        })
        return obj_dict

