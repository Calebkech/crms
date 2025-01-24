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