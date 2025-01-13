from sqlalchemy import Float, String, ForeignKey
from .base_model import BaseModel
from extensions import db

class IncomeCategory(BaseModel):
    __tablename__ = 'income_category'

    name = db.Column(String(100), nullable=False)
    description = db.Column(String(255), nullable=True)

    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict.update({
            'name': self.name,
            'description': self.description
        })
        return obj_dict