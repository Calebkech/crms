from sqlalchemy import Float, String, Integer, Text
from .base_model import BaseModel
from extensions import db

class Customer(BaseModel):
    __tablename__ = 'customers'

    first_name = db.Column(String(100), nullable=False)  # Vendor name (required)
    last_name = db.Column(String(100), nullable=False)
    email = db.Column(String(100), nullable=False)  # Email address
    phone = db.Column(String(15), nullable=False)  # Phone number
    address = db.Column(String(255), nullable=False)  # Vendor's physical address
    description = db.Column(Text, nullable=True)  # Optional description of the vendor

    def to_dict(self):
        """Convert the Vendor object to a dictionary for easy serialization."""
        obj_dict = super().to_dict()  # Get fields from BaseModel
        obj_dict.update({
            'first_name': self.first_name,
            'las_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'description': self.description,
        })
        return obj_dict
