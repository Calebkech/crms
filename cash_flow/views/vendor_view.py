from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from cash_flow.models import Vendor
from .blueprint import cash_flow
import uuid

@cash_flow.route('/vendor', methods=['POST'])
def create_vendor():
    try:
        pass
    except Exception as e:
        pass

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