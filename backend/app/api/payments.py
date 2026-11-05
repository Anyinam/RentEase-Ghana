from decimal import Decimal, InvalidOperation

from flask import Blueprint, current_app, request
from flask_jwt_extended import get_jwt, get_jwt_identity

from app.api.decorators import roles_required
from app.extensions import db
from app.models import PaymentTransaction, Role, TenantLease

bp = Blueprint("payments", __name__)


@bp.post("/checkout")
@roles_required(Role.TENANT)
def create_checkout() -> tuple[dict[str, object], int]:
    data = request.get_json(silent=True) or {}
    try:
        lease_id = int(data["tenant_lease_id"])
        amount = Decimal(str(data["amount_ghs"]))
    except (KeyError, ValueError, InvalidOperation):
        return {"error": "tenant_lease_id and a valid amount_ghs are required"}, 400
    lease = db.session.get(TenantLease, lease_id)
    if lease is None or lease.tenant_id != int(get_jwt_identity()):
        return {"error": "Lease not found"}, 404
    if amount != lease.monthly_total_ghs:
        return {"error": "Payment amount must match the lease monthly installment"}, 422
    if not current_app.config["PAYSTACK_SECRET_KEY"]:
        return {"error": "Payment provider is not configured; no payment was initiated"}, 503

    return {"error": "Payment checkout adapter is not enabled; no payment was initiated"}, 501


@bp.post("/webhooks/paystack")
def paystack_webhook() -> tuple[str, int]:
    return "Webhook processing is not enabled until signature verification and provider reconciliation are configured.", 501


@bp.get("/<int:transaction_id>")
@roles_required(Role.TENANT, Role.ADMIN, Role.FINANCIAL_PARTNER)
def get_transaction(transaction_id: int) -> tuple[dict[str, object], int]:
    transaction = db.session.get(PaymentTransaction, transaction_id)
    if transaction is None:
        return {"error": "Transaction not found"}, 404
    if get_jwt_identity() and transaction.tenant_lease_id:
        lease = db.session.get(TenantLease, transaction.tenant_lease_id)
        if lease is None or (
            get_jwt().get("role") == Role.TENANT.value
            and lease.tenant_id != int(get_jwt_identity())
        ):
            return {"error": "Transaction not found"}, 404
    return {
        "id": transaction.id,
        "reference": transaction.provider_reference,
        "amount_ghs": float(transaction.amount_ghs),
        "currency": transaction.currency,
        "provider": transaction.provider,
        "status": transaction.status.value,
        "payment_type": transaction.payment_type,
        "created_at": transaction.created_at.isoformat(),
    }, 200
