from flask import jsonify, Blueprint, request
from cash_flow.models import Invoice
from .blueprint import cash_flow
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
from .utils import (
    logger, ERROR_MESSAGES, handle_duplicate_entry_contact, InvoiceCreateSchema,
    validate_with_pydantic, InvoiceUpdateSchema
)
import uuid

# dependency injection for database Session
def get_db_session():
    """ Dependency injection for database session."""
    return db.session

@cash_flow.route('/invoice', methods=['POST'])
def create_invoice():
    """
    Create a new invoice.
    """
    try:
        # Get data from the request
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": ERROR_MESSAGES['invalid_json']}), 400

        # Validate data using Pydantic
        is_valid, validated_data = validate_with_pydantic(InvoiceCreateSchema, data)
        if not is_valid:
            return jsonify({"error": "Validation failed", "details": validated_data}), 400

        # Create and save the new invoice
        new_invoice = Invoice(**validated_data)
        new_invoice.save(get_db_session())

        return jsonify({"message": "Invoice created successfully", "invoice": new_invoice.to_dict()}), 201

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/invoice', methods=['GET'])
def get_all_invoices():
    """
    Fetch all invoices.
    """
    try:
        # Fetch all invoices from the database
        invoices = Invoice.query.filter(Invoice.deleted_at.is_(None)).all()
        invoices_list = [invoice.to_dict() for invoice in invoices]

        return jsonify(invoices_list), 200

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/invoice/<string:invoice_id>', methods=['PUT'])
def update_invoice(invoice_id: str):
    """
    Update an existing invoice by its ID.
    """
    try:
        # Fetch the invoice from the database
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404

        # Get the request data
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": ERROR_MESSAGES['invalid_json']}), 400

        # Validate data using Pydantic
        is_valid, validated_data = validate_with_pydantic(InvoiceUpdateSchema, data)
        if not is_valid:
            return jsonify({"error": "Validation failed", "details": validated_data}), 400

        # Update invoice fields
        for field, value in validated_data.items():
            setattr(invoice, field, value)

        # Save the updated invoice
        invoice.save(get_db_session())

        return jsonify({"message": "Invoice updated successfully", "invoice": invoice.to_dict()}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/invoice/<string:invoice_id>', methods=['DELETE'])
def soft_delete_invoice(invoice_id: str):
    """
    Soft delete an invoice by its ID.
    """
    try:
        # Fetch the invoice from the database
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404

        # Check if the invoice has already been soft deleted
        if invoice.deleted_at is not None:
            return jsonify({"error": "Invoice has already been soft deleted"}), 400

        # Soft delete the invoice
        invoice.soft_delete(get_db_session())

        return jsonify({"message": "Invoice soft deleted successfully"}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/invoice/<string:invoice_id>/restore', methods=['POST'])
def restore_invoice(invoice_id: str):
    """
    Restore a soft-deleted invoice by its ID.
    """
    try:
        # Fetch the soft-deleted invoice
        invoice = Invoice.query.filter(Invoice.id == invoice_id, Invoice.deleted_at.isnot(None)).first()
        if not invoice:
            return jsonify({"error": "Invoice not found or not deleted"}), 404

        # Restore the invoice
        invoice.deleted_at = None
        get_db_session().commit()

        return jsonify({"message": "Invoice restored successfully"}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/invoice/<string:invoice_id>/delete', methods=['DELETE'])
def delete_invoice(invoice_id: str):
    """
    Permanently delete an invoice by its ID.
    """
    try:
        # Fetch the invoice from the database
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404

        # Permanently delete the invoice
        invoice.delete(get_db_session())

        return jsonify({"message": "Invoice permanently deleted successfully"}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500