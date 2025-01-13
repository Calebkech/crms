from flask import Blueprint, jsonify, request, current_app
from .models.transaction_model import Transaction
from extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

# Define a Blueprint for transaction routes
transaction_bp = Blueprint('transactions', __name__)

@transaction_bp.route('/create_new', methods=['POST'])
@jwt_required()
def create_transaction():
    """ 
    Create new transaction
     
    """
    try:

        data = request.get_json()
        amount = data.get('amount')
        description = data.get('description', '')

        current_user = get_jwt_identity()  # This assumes your JWT contains the user's id
        user_id = current_user.get('user_id')

        current_app.logger.debug(f"parsed data: {data}")

        if not user_id or not amount:
            return jsonify({"error": "user_id and amount are required"}), 400

        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            description=description
        )
        transaction.save(db.session)  # Save transaction using the session
        return jsonify(transaction.to_dict()), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transaction_bp.route('/transactions/<string:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    transaction = db.session.query(Transaction).get(transaction_id)
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404
    return jsonify(transaction.to_dict()), 200
