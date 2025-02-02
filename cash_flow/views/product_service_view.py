from flask import jsonify, Blueprint, request
from cash_flow.models import ProductService
from .blueprint import cash_flow
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import uuid

@cash_flow.route('/product_service', methodes=['POST'])
def create_product_service():
    """
    Create product or service 
    """
    try:
        pass
    except  Exception as e:
        pass
