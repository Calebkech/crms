from flask import jsonify, Blueprint, request
from cash_flow.models import Transfer
from .blueprint import cash_flow
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
from .utils import (
    logger, ERROR_MESSAGES, handle_duplicate_entry_contact, TransferCreateSchema,
    validate_with_pydantic, TransferUpdateSchema
)
import uuid

# dependency injection for database Session
def get_db_session():
    """ Dependency injection for database session."""
    return db.session

@cash_flow.route('/transfer', methods=['POST'])
def create_transfer():
    """
    Create a new transfer.
    """
    try:
        # Get data from the request
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": ERROR_MESSAGES['invalid_json']}), 400

        # Validate data using Pydantic
        is_valid, validated_data = validate_with_pydantic(TransferCreateSchema, data)
        if not is_valid:
            return jsonify({"error": "Validation failed", "details": validated_data}), 400

        # Create and save the new transfer
        new_transfer = Transfer(**validated_data)
        new_transfer.save(get_db_session())

        return jsonify({"message": "Transfer created successfully", "transfer": new_transfer.to_dict()}), 201

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/transfer', methods=['GET'])
def get_transfer():
    """
    Fetch all transfers.
    """
    try:
        # Fetch all transfers from the database
        transfers = Transfer.query.filter(Transfer.deleted_at.is_(None)).all()
        transfers_list = [transfer.to_dict() for transfer in transfers]

        return jsonify(transfers_list), 200

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/transfer/<string:transfer_id>', methods=['PUT'])
def update_transfer(transfer_id: str):
    """
    Update an existing transfer by its ID.
    """
    try:
        # Fetch the transfer from the database
        transfer = Transfer.query.get(transfer_id)
        if not transfer:
            return jsonify({"error": "Transfer not found"}), 404

        # Get the request data
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": ERROR_MESSAGES['invalid_json']}), 400

        # Validate data using Pydantic
        is_valid, validated_data = validate_with_pydantic(TransferUpdateSchema, data)
        if not is_valid:
            return jsonify({"error": "Validation failed", "details": validated_data}), 400

        # Update transfer fields
        for field, value in validated_data.items():
            setattr(transfer, field, value)

        # Save the updated transfer
        transfer.save(get_db_session())

        return jsonify({"message": "Transfer updated successfully", "transfer": transfer.to_dict()}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/transfer/<string:transfer_id>', methods=['DELETE'])
def soft_delete_transfer(transfer_id: str):
    """
    Soft delete a transfer by its ID.
    """
    try:
        # Fetch the transfer from the database
        transfer = Transfer.query.get(transfer_id)
        if not transfer:
            return jsonify({"error": "Transfer not found"}), 404

        # Check if the transfer has already been soft deleted
        if transfer.deleted_at is not None:
            return jsonify({"error": "Transfer has already been soft deleted"}), 400

        # Soft delete the transfer
        transfer.soft_delete(get_db_session())

        return jsonify({"message": "Transfer soft deleted successfully"}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/transfer/<string:transfer_id>/restore', methods=['POST'])
def restore_transfer(transfer_id: str):
    """
    Restore a soft-deleted transfer by its ID.
    """
    try:
        # Fetch the soft-deleted transfer
        transfer = Transfer.query.filter(Transfer.id == transfer_id, Transfer.deleted_at.isnot(None)).first()
        if not transfer:
            return jsonify({"error": "Transfer not found or not deleted"}), 404

        # Restore the transfer
        transfer.deleted_at = None
        get_db_session().commit()

        return jsonify({"message": "Transfer restored successfully"}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@cash_flow.route('/transfer/<string:transfer_id>/delete', methods=['DELETE'])
def delete_transfer(transfer_id: str):
    """
    Permanently delete a transfer by its ID.
    """
    try:
        # Fetch the transfer from the database
        transfer = Transfer.query.get(transfer_id)
        if not transfer:
            return jsonify({"error": "Transfer not found"}), 404

        # Permanently delete the transfer
        transfer.delete(get_db_session())

        return jsonify({"message": "Transfer permanently deleted successfully"}), 200

    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500