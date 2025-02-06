from flask import jsonify, Blueprint, request
from cash_flow.models import Payment
from .blueprint import cash_flow
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
from .utils import (
    logger, ERROR_MESSAGES, handle_duplicate_entry_contact, PaymentCreateSchema,
    validate_with_pydantic, PaymentUpdateSchema
)
import uuid

# dependency injection for database Session
def get_db_session():
    """ Dependency injection for database session."""
    return db.session

@cash_flow.route('/payment', methods=['POST'])
def create_payment():
    """
    Create a new payment.
    """
    try:
        # Get data from the request
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": ERROR_MESSAGES['invalid_json']}), 400

        # Validate data using Pydantic
        is_valid, validated_data = validate_with_pydantic(PaymentCreateSchema, data)
        if not is_valid:
            return jsonify({"error": "Validation failed", "details": validated_data}), 400

        # Create and save the new payment
        new_payment = Payment(**validated_data)
        new_payment.save(get_db_session())

        return jsonify({"message": "Payment created successfully", "payment": new_payment.to_dict()}), 201

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/payment', methods=['GET'])
def get_payment():
    """
    Fetch all payments.
    """
    try:
        # Fetch all payments from the database
        payments = Payment.query.filter(Payment.deleted_at.is_(None)).all()
        payments_list = [payment.to_dict() for payment in payments]

        return jsonify(payments_list), 200

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/payment/<string:payment_id>', methods=['PUT'])
def update_payment(payment_id: str):
    """
    Update an existing payment by its ID.
    """
    try:
        # Fetch the payment from the database
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({"error": "Payment not found"}), 404

        # Get the request data
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": ERROR_MESSAGES['invalid_json']}), 400

        # Validate data using Pydantic
        is_valid, validated_data = validate_with_pydantic(PaymentUpdateSchema, data)
        if not is_valid:
            return jsonify({"error": "Validation failed", "details": validated_data}), 400

        # Update payment fields
        for field, value in validated_data.items():
            setattr(payment, field, value)

        # Save the updated payment
        payment.save(get_db_session())

        return jsonify({"message": "Payment updated successfully", "payment": payment.to_dict()}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/payment/<string:payment_id>', methods=['DELETE'])
def soft_delete_payment(payment_id: str):
    """
    Soft delete a payment by its ID.
    """
    try:
        # Fetch the payment from the database
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({"error": "Payment not found"}), 404

        # Check if the payment has already been soft deleted
        if payment.deleted_at is not None:
            return jsonify({"error": "Payment has already been soft deleted"}), 400

        # Soft delete the payment
        payment.soft_delete(get_db_session())

        return jsonify({"message": "Payment soft deleted successfully"}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/payment/<string:payment_id>/restore', methods=['POST'])
def restore_payment(payment_id: str):
    """
    Restore a soft-deleted payment by its ID.
    """
    try:
        # Fetch the soft-deleted payment
        payment = Payment.query.filter(Payment.id == payment_id, Payment.deleted_at.isnot(None)).first()
        if not payment:
            return jsonify({"error": "Payment not found or not deleted"}), 404

        # Restore the payment
        payment.deleted_at = None
        get_db_session().commit()

        return jsonify({"message": "Payment restored successfully"}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/payment/<string:payment_id>/delete', methods=['DELETE'])
def delete_payment(payment_id: str):
    """
    Permanently delete a payment by its ID.
    """
    try:
        # Fetch the payment from the database
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({"error": "Payment not found"}), 404

        # Permanently delete the payment
        payment.delete(get_db_session())

        return jsonify({"message": "Payment permanently deleted successfully"}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500