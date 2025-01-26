from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from cash_flow.models import CustomerContact
from .blueprint import cash_flow

@cash_flow.route('/customer_contact', methods=['POST'])
def create_customer_contact():
    try:
        pass
    except Exception as e:
        pass

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