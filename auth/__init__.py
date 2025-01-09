from flask import Blueprint, jsonify
from auth.models import db, User, TokenBlocklist, ResetToken

auth_bp = Blueprint('auth', __name__)

#import auth routes to register them
from . import routes