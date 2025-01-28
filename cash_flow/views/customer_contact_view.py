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
    """
    Update customer contact details by ID
    """
    try:
        # Fetch customer contact from Db
        customer_contact = CustomerContact.query.get(customer_contact_id)
        if not customer_contact:
            return jsonify({"Error": "Customer Contact not found"}), 400
        
        # Get data form request
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"Error": "Invalid Json in Request Body"}), 400
        
        # Update Contact info if present in the request
        if 'contact_type' in data:
            customer_contact.contact_type = data['contact_type']
        if 'contact_value' in data:
            customer_contact.contact_value = data['contact_value']
        
        # Save Updated Data
        try:
            customer_contact.save(db.session)
        except Exception as db_error:
            db.session.rollback()
            return jsonify({"error": "Failed to Update customer Contact", "Details": str(db_error)}), 500
        return jsonify(customer_contact.to_dict()), 200
    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred", 
            "details": str(e)
        }), 500

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