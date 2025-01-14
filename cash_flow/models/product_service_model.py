from sqlalchemy import Float, String, Integer, Text
from .base_model import BaseModel
from extensions import db

class ProductService(BaseModel):
    __tablename__ = 'product_services'

    name = db.Column(String(100), nullable=False)  # Name of the product/service
    description = db.Column(Text, nullable=True)  # Description of the product/service
    price = db.Column(Float, nullable=False)  # Sale price
    cost = db.Column(Float, nullable=False)  # Cost of the product/service
    stock_quantity = db.Column(Integer, nullable=True)  # Optional: Inventory stock count

    def to_dict(self):
        """Convert the ProductService object to a dictionary for easy serialization."""
        obj_dict = super().to_dict()  # Get fields from BaseModel
        obj_dict.update({
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'cost': self.cost,
            'stock_quantity': self.stock_quantity,
        })
        return obj_dict
