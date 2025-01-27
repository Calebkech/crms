from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from cash_flow.models import CustomerContact
from .blueprint import cash_flow

@cash_flow.route('/customer_contact', methods=['POST'])
def create_customer_contact():
    try:
        # Get data from the request
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"Error": "Invalid JSON in Request Body"}), 400
    
        # Validate required fields
        required_fields = ['contact_type', 'contact_value']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f'Missing Required field(s): {", ".join(missing_fields)}'}), 400
        
        contact_type = data.get('contact_type')
        contact_value = data.get('contatc_value')

        existing_details = CustomerContact.query.filter(CustomerContact.contact_value == contact_value)
        if existing_details:
            return jsonify({"Error": "Contact Value Already Exist"}), 400
        
        # Create New Customer Contact
        new_customer_contact = CustomerContact(
            contact_type = contact_type,
            contact_value = contact_value
        )

        # Save Using the Basemodel Method
        new_customer_contact.save(db.session)
        return jsonify({"Message": "Contact saved Successfully"}), 200
    
    # just incase... reduce debug time
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error Occurred", "Details": str(e)}), 500
    
    except Exception as e:
        return jsonify({"error": "An Unexpected error Occurred", "Details": str(e)}), 500

@cash_flow.route('/customer_contact/<string:customer_contact_id>', methods=['GET'])
def get_customer_contacts(customer_contact_id):
    try:
        pass
    except Exception as e:
        pass

@cash_flow.route('/cutomer_contact/<string:customer_contact_id>', methods=['PUT'])
def update_customer_contact(customer_contact_id):
    try:
        pass
    except Exception as e:
        pass

@cash_flow.route('/customer_contact/<string:customer_contact_id>', methods=['DELETE'])
def soft_delete_customer_contact(customer_contact_id):
    try:
        pass
    except Exception as e:
        pass

@cash_flow.route('/customer_contact/<string:customer_contact_id>', methods=['POST'])
def restore_customer_contact(customer_contact_id):
    try:
        pass
    except Exception as e:
        pass
@cash_flow.route('/customer_contact/<string:customer_contact_id>', methods=['DELETE'])
def delete_customer_contact(customer_contact_id):
    try:
        pass
    except Exception as e:
        pass