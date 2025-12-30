"""
API v1 endpoints.
"""
from flask import Blueprint

# Create v1 blueprint
bp = Blueprint('api_v1', __name__, url_prefix='/api')

# Import routes to register them
from . import cases, activities, auth, dashboard

