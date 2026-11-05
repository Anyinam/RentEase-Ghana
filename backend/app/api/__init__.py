from flask import Flask

from app.api.auth import bp as auth_bp
from app.api.master_leases import bp as master_leases_bp
from app.api.payments import bp as payments_bp
from app.api.properties import bp as properties_bp
from app.api.tenant_leases import bp as tenant_leases_bp
from app.api.underwriting import bp as underwriting_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(properties_bp, url_prefix="/api/properties")
    app.register_blueprint(underwriting_bp, url_prefix="/api/underwriting")
    app.register_blueprint(master_leases_bp, url_prefix="/api/master-leases")
    app.register_blueprint(tenant_leases_bp, url_prefix="/api/tenant-leases")
    app.register_blueprint(payments_bp, url_prefix="/api/payments")
