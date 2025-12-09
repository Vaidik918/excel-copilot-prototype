"""
Flask Blueprint routes for Excel Copilot API
Phase 1: Progressive route registration (only existing routes)
"""

from flask import Blueprint
from .health import health_bp

# Add other imports as you create files:
# from .upload import upload_bp
# from .analyze import analyze_bp
# from .execute import execute_bp
# from .download import download_bp

def register_routes(app):
    """
    Register all blueprints with Flask app.
    Add more as you implement routes.
    """
    app.register_blueprint(health_bp, url_prefix='')
    
    # Uncomment as you create files:
    # app.register_blueprint(upload_bp, url_prefix='/api')
    # app.register_blueprint(analyze_bp, url_prefix='/api')
    # app.register_blueprint(execute_bp, url_prefix='/api')
    # app.register_blueprint(download_bp, url_prefix='/api')
    
    print("✅ Routes registered: health")
