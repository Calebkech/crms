from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from cash_flow.models import Vendor
from .blueprint import cash_flow
from .utils import (
    logger, ERROR_MESSAGES, validate_required_fields, handle_duplicate_entry,
    VendorCreateSchema, VendorUpdateSchema, validate_with_pydantic
)
import uuid
from typing import Dict, Optional, Type

# Dependency Injection for Database Session
def get_db_session():
    """Dependency injection for database session."""
    return db.session

@cash_flow.route('/vendor', methods=['POST'])
def create_vendor():
    """
    Create a new vendor.
    """
    try:
        # Get data from the request
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": ERROR_MESSAGES['invalid_json']}), 400

        # Validate data using Pydantic
        is_valid, validated_data = validate_with_pydantic(VendorCreateSchema, data)
        if not is_valid:
            return jsonify({"error": "Validation failed", "details": validated_data}), 400

        # Check for duplicate email or phone
        is_duplicate, duplicate_message = handle_duplicate_entry(
            Vendor, email=validated_data.get('email'), phone=validated_data.get('phone')
        )
        if is_duplicate:
            return jsonify({"error": duplicate_message}), 400

        # Create and save the new vendor
        new_vendor = Vendor(**validated_data)
        new_vendor.save(get_db_session())

        return jsonify({"message": "Vendor created successfully"}), 201

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/vendor', methods=['GET'])
def get_vendors():
    """
    Fetch all vendors except the soft-deleted ones.
    """
    try:
        vendors = Vendor.query.filter(Vendor.deleted_at.is_(None)).all()
        vendors_list = [vendor.to_dict() for vendor in vendors]
        return jsonify(vendors_list), 200
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/vendor/<string:vendor_id>', methods=['PUT'])
def update_vendor(vendor_id: str):
    """
    Update a vendor's details by its ID.
    """
    try:
        # Fetch vendor from the database
        vendor = Vendor.query.get(vendor_id)
        if not vendor:
            return jsonify({"error": "Vendor not found"}), 404

        # Get the request data
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": ERROR_MESSAGES['invalid_json']}), 400

        # Validate data using Pydantic
        is_valid, validated_data = validate_with_pydantic(VendorUpdateSchema, data)
        if not is_valid:
            return jsonify({"error": "Validation failed", "details": validated_data}), 400

        # Update vendor fields
        for field, value in validated_data.items():
            setattr(vendor, field, value)

        # Save the updated vendor
        vendor.save(get_db_session())
        return jsonify(vendor.to_dict()), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/vendor/<string:vendor_id>', methods=['DELETE'])
def soft_delete_vendor(vendor_id: str):
    """
    Soft delete a vendor by its UUID.
    """
    try:
        # Fetch the vendor using active_query
        vendor = Vendor.active_query().filter_by(id=vendor_id).first()
        if not vendor:
            return jsonify({"error": "Vendor not found"}), 404
        
        # Check if the vendor has already been soft deleted
        if vendor.deleted_at is not None:
            return jsonify({"error": "Vendor has already been soft deleted"}), 400

        # Soft delete the vendor
        vendor.soft_delete(get_db_session())
        return jsonify({"message": "Vendor soft-deleted successfully"}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/vendor/<string:vendor_id>', methods=['POST'])
def restore_vendor(vendor_id: str):
    """
    Restore a soft-deleted vendor by its UUID.
    """
    try:
        # Fetch the soft-deleted vendor
        vendor = Vendor.query.filter(Vendor.id == vendor_id, Vendor.deleted_at.isnot(None)).first()
        if not vendor:
            return jsonify({"error": "Vendor not found or not deleted"}), 404

        # Restore the vendor by clearing the deleted_at timestamp
        vendor.deleted_at = None
        get_db_session().commit()
        return jsonify({"message": "Vendor restored successfully"}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/vendor/<string:vendor_id>/delete', methods=['DELETE'])
def delete_vendor(vendor_id: str):
    """
    Permanently delete a vendor by its UUID.
    """
    try:
        # Validate UUID format
        try:
            uuid.UUID(vendor_id)
        except ValueError:
            return jsonify({"error": "Invalid UUID"}), 400

        # Fetch the vendor from the database
        vendor = Vendor.query.get(vendor_id)
        if not vendor:
            return jsonify({"error": "Vendor not found"}), 404

        # Permanently delete the vendor
        vendor.delete(get_db_session())
        return jsonify({"message": "Vendor deleted successfully"}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500