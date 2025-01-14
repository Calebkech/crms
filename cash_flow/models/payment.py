from sqlalchemy import Float, String, Integer, Date, Enum
from .base_model import BaseModel
from extensions import db
import enum

class PaymentMethod(enum.Enum):
    CASH = "cash"
    BANK = "bank"
    CREDIT = "credit"

class Payment(BaseModel):
    __tablename__ = 'payments'

    invoice_id = db.Column(String(36), db.ForeignKey('invoices.id'), nullable=False)  # Reference to Invoice table
    payment_date = db.Column(Date, nullable=False)  # Date of payment
    amount = db.Column(Float, nullable=False)  # Amount paid
    payment_method = db.Column(Enum(PaymentMethod), nullable=False)  # Payment method
    account_id = db.Column(String(36), db.ForeignKey('accounts.id'), nullable=True)  # Reference to an account (optional)

    invoice = db.relationship('Invoice', backref=db.backref('payments', lazy=True))  # Relationship to Invoice
    account = db.relationship('Account', backref=db.backref('payments', lazy=True))  # Relationship to Account

    def to_dict(self):
        """Convert the Payment object to a dictionary for easy serialization."""
        obj_dict = super().to_dict()  # Get fields from BaseModel
        obj_dict.update({
            'invoice_id': self.invoice_id,
            'payment_date': self.payment_date,
            'amount': self.amount,
            'payment_method': self.payment_method.value,  # Use the value of the Enum
            'account_id': self.account_id,
        })
        return obj_dict
