from sqlalchemy import String, DateTime
from extensions import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the audit log entry
    action = db.Column(String(255), nullable=False)  # Action performed (e.g., 'created', 'updated', 'deleted')
    user_id = db.Column(String(36), db.ForeignKey('users.id'), nullable=False)  # User who performed the action
    entity_id = db.Column(String(36), nullable=False)  # ID of the entity affected
    entity_type = db.Column(String(100), nullable=False)  # Type of entity (e.g., 'Transaction', 'Account', etc.)
    timestamp = db.Column(DateTime, default=datetime.utcnow, nullable=False)  # Time of the action

    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))

    def to_dict(self):
        """Convert the AuditLog object to a dictionary for easy serialization."""
        return {
            'id': self.id,
            'action': self.action,
            'user_id': self.user_id,
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'timestamp': self.timestamp,
        }
