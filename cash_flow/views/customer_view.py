from flask import request, jsonify, Blueprint
from sqlalchemy.exc import SQLAlchemyError
from cash_flow.models import Customer
from extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from .blueprint import cash_flow
import uuid

@cash_flow.route('/new_customer', methods=['POST'])
def create_customer():
    try:
        # Get data from the request
        data = request.get_json()

        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'phone', 'address']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing Required field(s): {", ".join(missing_fields)}'}), 400
        
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone = data.get('phone')
        address = data.get('address')

        # Validate user Email and phone number
        existing_details = Customer.query.filter((Customer.email == email) | (Customer.phone == phone)).first()
        if existing_details:
            if existing_details.email == email and existing_details.phone == phone:
                return jsonify({'msg': 'Both Email and phone number area already registered, Kindly use different ones'}), 400
            if existing_details.email == email:
                return jsonify({"msg": "Email is already registered, Kindly use a different email" }), 400
            if existing_details.phone == phone:
                return jsonify({"msg": "Phone Number is already registered, Kindly use a differrent Phone Number" }), 400

        #Create New User
        new_customer = Customer(
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone = phone,
            address = address
        )

        # Save using Basemodel method
        new_customer.save(db.session)

        return jsonify({'message': 'Registration Success'})
    #just incase, and reduce debuging time
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'detailes': str(e)}), 500

@cash_flow.route('/view_customers', methods = ['GET'])
def get_all_customers():
    """
    Fetch all customers in the db eccept the soft deleted ones
    """
    try:
        # first fileter customers where deleted_at is None
        customers = Customer.query.filter(Customer.deleted_at.is_(None)).all()
        # serialize customers
        customers_list = [customer.to_dict() for customer in customers]
        return jsonify(customers_list), 200
    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred", 
            "details": str(e)
        }), 500
    
@cash_flow.route('/cutomer/<string:customer_id>/soft_delete', methods=['DELETE'])
def soft_delete_customer(customer_id):
    """
    Soft delete customer by its UUID
    """
    try:
        # Fetch the customer using active_querry
        customer = Customer.active_query().filter_by(id = customer_id).first()
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        # Soft delete the customer
        customer.soft_delete(db.session)
        return jsonify({"message": "Customer soft-deleted successfully"}), 200
    
    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500
    
@cash_flow.route('/cutomer/<string:customer_id>/restore_customer', methods=['POST'])
def restore_customer(customer_id):
    """
    Restore a soft-delete customer by its UUID
    """
    try:
        # Fetch the soft-deleted cutomer
        customer = Customer.query.filter(Customer.id == customer_id, Customer.deleted_at.isnot(None)).first()

        if not customer:
            return jsonify({"error": "Customer not found or not deleted"}), 404
        
        # Restore the Customer by clearing the deleted_at timestamp
        customer.deleted_at = None 
        db.session.commit()
        
        return jsonify({"message": "Customer restored Successfully"}), 200
    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500