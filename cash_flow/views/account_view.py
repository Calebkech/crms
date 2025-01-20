from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from cash_flow.models.account_model import Account
from extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
from .blueprint import cash_flow

@cash_flow.route('/create_account', methods=['POST'])
#@jwt_required()
def create_account():
    try:
        # Get JSON data from the request
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'balance', 'account_type']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        name = data.get('name')
        balance = data.get('balance')
        account_type = data.get('account_type')  # e.g., 'savings', 'checking'

        # Validate account type
        if account_type not in ['savings', 'checking']:
            return jsonify({'error': 'Invalid account type. Valid types are "savings" or "checking".'}), 400

        # Validate initial balance
        if balance < 0:
            return jsonify({'error': 'Initial balance cannot be negative'}), 400

        # Create a new account
        new_account = Account(
            name=name,
            balance=balance,
            account_type=account_type
        )

        # Use the save method from BaseModel
        new_account.save(db.session)

        return jsonify({'message': 'Account created successfully', 'account': new_account.to_dict()}), 201

    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback in case of an error
        return jsonify({'error': 'Database error occurred', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500

@cash_flow.route('/accounts', methods=['GET'])
def get_all_accounts():
    """
    Fetch and return all accounts in the database, excluding soft-deleted ones.
    """
    try:
        # Filter accounts where deleted_at is None
        accounts = Account.query.filter(Account.deleted_at.is_(None)).all()
        accounts_list = [account.to_dict() for account in accounts]  # Serialize accounts
        return jsonify(accounts_list), 200
    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500

@cash_flow.route('/accounts/<string:account_id>', methods=['PUT'])
def update_account(account_id):
    """
    Update an account's details by its ID.
    """
    try:
        # Fetch account from the database
        account = Account.query.get(account_id)
        if not account:
            return jsonify({"error": "Account not found"}), 404

        # Get the request data
        data = request.get_json()

        # Update account fields if present in the request
        if 'name' in data:
            account.name = data['name']
        if 'description' in data:
            account.description = data['description']
        if 'balance' in data:
            account.balance = float(data['balance'])
        if 'account_type' in data:
            account.account_type = data['account_type']

        # Save the updated account
        account.save(db.session)

        return jsonify(account.to_dict()), 200

    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500

@cash_flow.route('/accounts/<string:account_id>/soft_delete', methods=['DELETE'])
def soft_delete_account(account_id):
    """
    Soft delete an account by its UUID.
    """
    try:
        # Fetch the account using active_query
        account = Account.active_query().filter_by(id=account_id).first()
        if not account:
            return jsonify({"error": "Account not found"}), 404

        # Soft delete the account
        account.soft_delete(db.session)
        return jsonify({"message": "Account soft-deleted successfully"}), 200

    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500

@cash_flow.route('/accounts/<string:account_id>/restore', methods=['POST'])
def restore_account(account_id):
    """
    Restore a soft-deleted account by its UUID.
    """
    try:
        # Fetch the soft-deleted account
        account = Account.query.filter(Account.id == account_id, Account.deleted_at.isnot(None)).first()
        
        if not account:
            return jsonify({"error": "Account not found or not deleted"}), 404

        # Restore the account
        account.deleted_at = None  # Clear the deleted_at timestamp
        db.session.commit()

        return jsonify({"message": "Account restored successfully"}), 200

    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500

@cash_flow.route('/accounts/<string:account_id>/hard_delete', methods=['DELETE'])
def delete_account(account_id):
    """
    Delete an account by its UUID.
    """
    try:
        # Validate UUID format
        try:
            uuid_obj = uuid.UUID(account_id)
        except ValueError:
            return jsonify({"error": "Invalid UUID format"}), 400

        # Fetch the account from the database
        account = Account.query.get(account_id)
        if not account:
            return jsonify({"error": "Account not found"}), 404

        # Delete the account using BaseModel's delete method
        account.delete(db.session)

        return jsonify({"message": "Account deleted successfully"}), 200

    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500
