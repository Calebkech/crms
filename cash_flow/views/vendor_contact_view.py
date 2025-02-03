from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from cash_flow.models import VendorContact
from cash_flow.models import Vendor
from .blueprint import cash_flow
from .utils import (
    logger, ERROR_MESSAGES, validate_with_pydantic,
    VendorContactCreateSchema, VendorContactUpdateSchema, validate_vendor_id, handle_duplicate_entry_contact
)
import uuid
from typing import Dict, Optional

# Dependency Injection for Database Session
def get_db_session():
    """Dependency injection for database session."""
    return db.session

@cash_flow.route('/vendor_contact', methods=['POST'])
def create_vendor_contact():
    """
    Create a new vendor contact.
    """
    try:
        # Get data from the request
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": ERROR_MESSAGES['invalid_json']}), 400

        # Validate data using Pydantic
        is_valid, validated_data = validate_with_pydantic(VendorContactCreateSchema, data)
        if not is_valid:
            return jsonify({"error": "Validation failed", "details": validated_data}), 400

        # Validate vendor_id
        vendor_id = validated_data.get('vendor_id')
        is_vendor_valid, error_message = validate_vendor_id(vendor_id)
        if not is_vendor_valid:
            return jsonify({"error": error_message}), 404

        # Check for duplicate contact_value (email or phone)
        contact_value = validated_data.get('contact_value')
        is_duplicate, duplicate_message = handle_duplicate_entry_contact(
            VendorContact,
            field='contact_value',
            value=contact_value
        )
        if is_duplicate:
            return jsonify({"error": duplicate_message}), 400

        # Create and save the new vendor contact
        new_contact = VendorContact(**validated_data)
        new_contact.save(db.session)

        return jsonify({"message": "Vendor contact created successfully"}), 201

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/vendor_contact', methods=['GET'])
def get_vendor_contacts():
    """
    Fetch all vendor contacts except the soft-deleted ones.
    """
    try:
        vendor_contacts = VendorContact.query.filter(VendorContact.deleted_at.is_(None)).all()
        vendor_contact_list = [vendor_contact.to_dict() for vendor_contact in vendor_contacts]
        return jsonify(vendor_contact_list), 200
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/vendor_contact/<string:vendor_contact_id>', methods=['PUT'])
def update_vendor_contact(vendor_contact_id: str):
    """
    Update a vendor contact by its ID.
    """
    try:
        # Fetch the vendor contact from the database
        contact = VendorContact.query.get(vendor_contact_id)
        if not contact:
            return jsonify({"error": "Vendor contact not found"}), 404

        # Get the request data
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": ERROR_MESSAGES['invalid_json']}), 400

        # Validate data using Pydantic
        is_valid, validated_data = validate_with_pydantic(VendorContactUpdateSchema, data)
        if not is_valid:
            return jsonify({"error": "Validation failed", "details": validated_data}), 400
        
        # Validate vendor_id
        vendor_id = validated_data.get('vendor_id')
        is_vendor_valid, error_message = validate_vendor_id(vendor_id)
        if not is_vendor_valid:
            return jsonify({"error": error_message}), 404

        # Check for duplicate contact_value (email or phone)
        contact_value = validated_data.get('contact_value')
        is_duplicate, duplicate_message = handle_duplicate_entry_contact(
            VendorContact,
            field='contact_value',
            value=contact_value
        )
        if is_duplicate:
            return jsonify({"error": duplicate_message}), 400

        # Update vendor contact fields
        for field, value in validated_data.items():
            setattr(contact, field, value)

        # Save the updated vendor contact
        contact.save(get_db_session())
        return jsonify(contact.to_dict()), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/vendor_contact/<string:vendor_contact_id>', methods=['DELETE'])
def soft_delete_vendor_contact(vendor_contact_id: str):
    """
    Soft delete a vendor contact by its ID.
    """
    try:
        # Fetch the vendor contact from the database
        contact = VendorContact.query.get(vendor_contact_id)
        if not contact:
            return jsonify({"error": "Vendor contact not found"}), 404
        
        # Check if the contact has already been soft deleted
        if contact.deleted_at is not None:
            return jsonify({"error": "Vendor contact has already been soft deleted"}), 400

        # Soft delete the vendor contact
        contact.soft_delete(get_db_session())
        return jsonify({"message": "Vendor contact soft-deleted successfully"}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/vendor_contact/<string:vendor_contact_id>', methods=['POST'])
def restore_vendor_contact(vendor_contact_id: str):
    """
    Restore a soft-deleted vendor contact by its ID.
    """
    try:
        # Fetch the soft-deleted vendor contact
        contact = VendorContact.query.filter(
            VendorContact.id == vendor_contact_id,
            VendorContact.deleted_at.isnot(None)
        ).first()
        if not contact:
            return jsonify({"error": "Vendor contact not found or not deleted"}), 404

        # Restore the vendor contact
        contact.deleted_at = None
        get_db_session().commit()
        return jsonify({"message": "Vendor contact restored successfully"}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/vendor_contact/<string:vendor_contact_id>/delete', methods=['DELETE'])
def delete_vendor_contact(vendor_contact_id: str):
    """
    Permanently delete a vendor contact by its ID.
    """
    try:
        # Validate UUID format
        try:
            uuid.UUID(vendor_contact_id)
        except ValueError:
            return jsonify({"error": "Invalid UUID"}), 400

        # Fetch the vendor contact from the database
        contact = VendorContact.query.get(vendor_contact_id)
        if not contact:
            return jsonify({"error": "Vendor contact not found"}), 404

        # Permanently delete the vendor contact
        contact.delete(get_db_session())
        return jsonify({"message": "Vendor contact deleted successfully"}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500