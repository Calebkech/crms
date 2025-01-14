from sqlalchemy import Float, String, Date, Enum, ForeignKey
from .base_model import BaseModel
from extensions import db
import enum

class InvoiceStatus(enum.Enum):
    PAID = "paid"
    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"

class Invoice(BaseModel):
    __tablename__ = 'invoices'

    customer_id = db.Column(String(36), db.ForeignKey('customers.id'), nullable=False)  # Reference to Customer table
    total_amount = db.Column(Float, nullable=False)  # Total amount of the invoice
    status = db.Column(Enum(InvoiceStatus), default=InvoiceStatus.UNPAID, nullable=False)  # Invoice status
    due_date = db.Column(Date, nullable=False)  # Due date for the invoice

    customer = db.relationship('Customer', backref=db.backref('invoices', lazy=True))  # Relationship to Customer
    payments = db.relationship('Payment', backref='invoice', lazy=True)  # Relationship to Payments

    def calculate_balance_due(self):
        """Calculate the outstanding balance for the invoice."""
        total_paid = sum(payment.amount for payment in self.payments)
        return self.total_amount - total_paid

    def update_status(self):
        """Update the status of the invoice based on payments."""
        balance_due = self.calculate_balance_due()
        if balance_due == 0:
            self.status = InvoiceStatus.PAID
        elif balance_due < self.total_amount:
            self.status = InvoiceStatus.PARTIALLY_PAID
        else:
            self.status = InvoiceStatus.UNPAID

    def to_dict(self):
        """Convert the Invoice object to a dictionary for easy serialization."""
        obj_dict = super().to_dict()  # Get fields from BaseModel
        obj_dict.update({
            'customer_id': self.customer_id,
            'total_amount': self.total_amount,
            'status': self.status.value,  # Serialize Enum value
            'due_date': self.due_date,
            'balance_due': self.calculate_balance_due(),  # Include balance_due
        })
        return obj_dict
