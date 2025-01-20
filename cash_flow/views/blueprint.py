from flask import Blueprint

#the blueprint below will be used by all routes under cash_flow
cash_flow = Blueprint('cashflow', __name__)