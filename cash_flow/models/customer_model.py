from sqlalchemy import Float, String, Integer, Text
from .base_model import BaseModel
from extensions import db

class Customer(BaseModel):
    __tablename__ = 'customers'

    name = db.Column(String(100), nullable=False)  # Vendor name (required)
    email = db.Column(String(100), nullable=True)  # Email address
    phone = db.Column(String(15), nullable=True)  # Phone number
    address = db.Column(String(255), nullable=True)  # Vendor's physical address
    description = db.Column(Text, nullable=True)  # Optional description of the vendor

    def to_dict(self):
        """Convert the Vendor object to a dictionary for easy serialization."""
        obj_dict = super().to_dict()  # Get fields from BaseModel
        obj_dict.update({
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'description': self.description,
        })
        return obj_dict
