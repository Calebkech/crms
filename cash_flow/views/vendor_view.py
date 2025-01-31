from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from cash_flow.models import Vendor
from .blueprint import cash_flow
import uuid

@cash_flow.route('/vendor', methods=['POST'])
def create_vendor():
    """"
    Create new Vendor
    """
    try:
        # Get data from the request
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Invalid JSON in request body"}), 400

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
        description = data.get('description')

        # Validate user Email and phone number
        existing_details = Vendor.query.filter((Vendor.email == email) | (Vendor.phone == phone)).first()
        if existing_details:
            if existing_details.email == email and existing_details.phone == phone:
                return jsonify({'msg': 'Both Email and phone number area already registered, Kindly use different ones'}), 400
            if existing_details.email == email:
                return jsonify({"msg": "Email is already registered, Kindly use a different email" }), 400
            if existing_details.phone == phone:
                return jsonify({"msg": "Phone Number is already registered, Kindly use a differrent Phone Number" }), 400

        #Create New User
        new_Vendor = Vendor(
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone = phone,
            address = address,
            description = description
        )

        # Save using Basemodel method
        new_Vendor.save(db.session)

        return jsonify({'message': 'Registration Success'}), 200
    #just incase, and reduce debuging time
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'detailes': str(e)}), 500

@cash_flow.route('/vendor', methods=['GET'])
def get_vendors():
    try:
        pass
    except Exception as e:
        pass

@cash_flow.route('/vendor/<string:vendor_id>', methods=['PUTS'])
def update_vendor(vendor_id):
    try:
        pass
    except Exception as e:
        pass

@cash_flow.route('/vendor/<string:vendor_id>', methods=['DELETE'])
def soft_delete_vendor(vendor_id):
    try:
        pass
    except Exception as e:
        pass

@cash_flow.route('/vendor/<string:vendor_id>', methods=['POST'])
def restore_vendor(vendor_id):
    try:
        pass
    except Exception as e:
        pass

@cash_flow.route('/vendor/<string:vendor_id>', methods=['DELETE'])
def delete_vendor(vendor_id):
    try:
        pass
    except Exception as e:
        pass