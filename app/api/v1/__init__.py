"""
API v1 endpoints.
"""

from flask import Blueprint

# Create v1 blueprint
bp = Blueprint("api_v1", __name__, url_prefix="/api")

# Import routes to register them with the blueprint
# These modules will use 'from . import bp' to get this blueprint
from . import cases, activities
