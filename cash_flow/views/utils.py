# utils.py
import logging
from typing import Dict, List, Optional, Type
from pydantic import BaseModel, EmailStr, ValidationError
from sqlalchemy.orm import Query
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define error messages
ERROR_MESSAGES = {
    'invalid_json': 'Invalid JSON in request body',
    'missing_fields': 'Missing Required field(s): {}',
    'email_exists': 'Email is already registered, Kindly use a different email',
    'phone_exists': 'Phone Number is already registered, Kindly use a different Phone Number',
}

# Pydantic Schemas for Data Validation
class VendorCreateSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address: str
    description: Optional[str] = None

class VendorUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None

# Utility Functions
def validate_required_fields(data: Dict, required_fields: List[str]) -> tuple[bool, Optional[str]]:
    """
    Validate that all required fields are present in the data.
    
    Args:
        data (Dict): The data to validate.
        required_fields (List[str]): List of required fields.
    
    Returns:
        tuple[bool, Optional[str]]: (True, None) if valid, (False, error_message) if invalid.
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, ERROR_MESSAGES['missing_fields'].format(", ".join(missing_fields))
    return True, None

def handle_duplicate_entry(model: Type, email: Optional[str] = None, phone: Optional[str] = None) -> tuple[bool, Optional[str]]:
    """
    Check if a record with the given email or phone already exists in the database.
    
    Args:
        model: The SQLAlchemy model to query.
        email (Optional[str]): The email to check.
        phone (Optional[str]): The phone number to check.
    
    Returns:
        tuple[bool, Optional[str]]: (True, error_message) if duplicate exists, (False, None) otherwise.
    """
    query: Query = model.query
    if email and phone:
        existing_record = query.filter((model.email == email) | (model.phone == phone)).first()
    elif email:
        existing_record = query.filter(model.email == email).first()
    elif phone:
        existing_record = query.filter(model.phone == phone).first()
    else:
        return False, None

    if existing_record:
        if existing_record.email == email and existing_record.phone == phone:
            return True, 'Both Email and phone number are already registered'
        if existing_record.email == email:
            return True, ERROR_MESSAGES['email_exists']
        if existing_record.phone == phone:
            return True, ERROR_MESSAGES['phone_exists']
    return False, None

def validate_with_pydantic(schema: Type[BaseModel], data: Dict) -> tuple[bool, Optional[Dict]]:
    """
    Validate data using a Pydantic schema.
    
    Args:
        schema: The Pydantic schema to use for validation.
        data (Dict): The data to validate.
    
    Returns:
        tuple[bool, Optional[Dict]]: (True, validated_data) if valid, (False, error_details) if invalid.
    """
    try:
        validated_data = schema(**data).dict(exclude_unset=True)
        return True, validated_data
    except ValidationError as e:
        return False, e.errors()