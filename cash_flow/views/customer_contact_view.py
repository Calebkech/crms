from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from cash_flow.models import CustomerContact
from .blueprint import cash_flow
import uuid

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
    """
    Fetch all the customer contacts except the soft deleted
    """
    try:
        # Filter contact where deleted_at is None
        customer_contacts = CustomerContact.query.filter(CustomerContact.deleted_at.is_(None)).all()

        #serialize customers
        customer_contact_list = [customer_contacts.to_dict() for customer_contact in customer_contacts]
        return jsonify(customer_contact_list), 200
    
    except Exception as e:
        return jsonify({
            "Error": "An Unxpected error Occurred",
            "details": str(e)
        }), 500
    

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
    """
    Soft delete a customer contact by its Id
    """
    try:
        # fetct the conatact using active querry
        customer_contact = CustomerContact.active_query().filter_by(id = customer_contact_id).first()
        if not customer_contact:
            return jsonify({"error": "Contact not found"}), 404
        
        # soft delete the contact if customer_contact is not None
        customer_contact.soft_delete(db.session)
        return jsonify({"message": "Contact Soft Deleted successfully"}), 200
    
    except Exception as e:
        return jsonify({
            "error": "an unexpected error occured",
            "details": str(e)
        }), 500

@cash_flow.route('/customer_contact/<string:customer_contact_id>', methods=['POST'])
def restore_customer_contact(customer_contact_id):
    """
    Restore soft deleted contact by its Id
    """
    try:
        # Fetch soft deleted conatact 
        customer_contact = CustomerContact.query.filter(CustomerContact.id == customer_contact_id, CustomerContact.deleted_at.isnot(None)).first()

        if not customer_contact:
            return jsonify({"error": "Contact not found"}), 404
        
        # Restore the contact by setting deleted_at timestamp to Non
        customer_contact.deleted_at = None
        db.session.commit()

        return jsonify({"message": "Contact restored successfully"}), 200
    
    except Exception as e:
        return jsonify({
            "error": "an unexpected error occured",
            "details": str(e)
        }), 500

@cash_flow.route('/customer_contact/<string:customer_contact_id>', methods=['DELETE'])
def delete_customer_contact(customer_contact_id):
    """
    Delete contact by its Id
    """
    try:
        try:

            # Validate UUID Format
            uuid_obj = uuid.UUID(customer_contact_id)
        except ValueError:
            return jsonify({"error": "Invalid Contact Id"})
        
        # Fetch contact to be deleted form db
        customer_contact = CustomerContact.query.get(customer_contact_id)
        if not customer_contact:
            return jsonify({"error": "contact not found"}), 404
        
        # Delete contact using basemodel's delete
        customer_contact.delete(db.session)
        return jsonify({"error": "contact deleted successfully"}), 200
    except Exception as e:
        return jsonify({
            "error": "an unexpected error occured",
            "Details": str(e)
        }), 500