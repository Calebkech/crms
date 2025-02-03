from flask import jsonify, Blueprint, request
from cash_flow.models import ProductService
from .blueprint import cash_flow
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
from .utils import (
    logger, ERROR_MESSAGES, handle_duplicate_entry_contact, ProductServiceCreateSchema,
    validate_with_pydantic, ProductServiceUpdateSchema
)
import uuid

# dependency injection for database Session
def get_db_session():
    """ Dependency injection for database session."""
    return db.session

@cash_flow.route('/product_service', methods=['POST'])
def create_product_service():
    """
    Create product or service 
    """
    try:
        product_service_data = request.get_json(silent=True)
        if product_service_data is None:
            return jsonify({"error": ERROR_MESSAGES['invalid_json']}), 400
        
        # validate data using Pydantic
        is_valid, validated_data = validate_with_pydantic(ProductServiceCreateSchema, product_service_data)
        if not is_valid:
            return jsonify({"error": "Verification faild", "details": validated_data}), 400
        
        # check for duplicate product or service names befor saving
        name_value = validated_data.get('name')
        is_duplicate, duplicate_message = handle_duplicate_entry_contact(
            ProductService,
            field='name',
            value=name_value
        )

        if is_duplicate:
            return jsonify({"error": duplicate_message}), 400
        
        # Create and save the new vendor
        new_product_service = ProductService(**validated_data)
        new_product_service.save(get_db_session())

        return jsonify({"message": "Product/Service Created successfully"}), 201
    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f"Database error occured: {str(e)}")
        return jsonify({"error": "Database error occured", "details": str(e)}), 500
    except  Exception as e:
        logger.error(f"An unexpected error occured: {str(e)}")
        return jsonify({"error": "An unxpected error occured", "details": str(e)}), 500


@cash_flow.route('/get_all', methods=['GET'])
def get_all():
    """
    fetch all products and services in the db
    """
    try:
        products_services = ProductService.query.filter(ProductService.deleted_at.is_(None)).all()
        products_services_list = [products_service.to_dict() for products_service in products_services]
        return jsonify(products_services_list), 200
    
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@cash_flow.route('/product_service/<string:product_service_id>', methods=['PUT'])
def update_product_service(product_service_id: str):
    """
    update product and service by its id
    """
    try:
        #fetch and validate user from database
        product_service = ProductService.query.get(product_service_id)
        if not product_service_id:
            return jsonify({"error": "Product or service/service not found"}), 404
        
        #Get the request data
        product_service_data = request.get_json(silent=True)
        if product_service_data is None:
            return jsonify({"error": ERROR_MESSAGES['invalid_json']}), 400
        
        # validate data using Pydantic
        is_valid, validate_data = validate_with_pydantic(ProductServiceUpdateSchema, product_service_data)
        if not is_valid:
            return jsonify({"error": "Validation faild", "details": validate_data}), 400
        
        #check for duplicate name
        name_value = validate_data.get('name')
        is_duplicate, duplicate_message = handle_duplicate_entry_contact(
            ProductService,
            field='name',
            value=name_value
        )
        if is_duplicate:
            return jsonify({"error": duplicate_message}), 400
        
        #updated product or service fields
        for field, value in validate_data.items():
            setattr(product_service, field, value)

        # now save the updated product or service fields
        product_service.save(get_db_session())
        return jsonify(product_service.to_dict()), 200
    
    except SQLAlchemyError as e:
        get_db_session().rollback()
        logger.error(f'Database error occured: {str(e)}')
        return jsonify({"error": "An unexpected error occured", "details": str(e)}), 500
    
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500