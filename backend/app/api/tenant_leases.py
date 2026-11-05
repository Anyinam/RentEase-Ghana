from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import select

from app.api.decorators import roles_required
from app.extensions import db
from app.models import LeaseStatus, MasterLease, Property, Role, TenantLease, UnderwritingProfile

bp = Blueprint("tenant_leases", __name__)


@bp.post("")
@roles_required(Role.TENANT, Role.ADMIN)
def create_tenant_lease() -> tuple[dict[str, object], int]:
    data = request.get_json(silent=True) or {}
    try:
        property_id = int(data["property_id"])
        start = date.fromisoformat(data["start_date"])
        end = date.fromisoformat(data["end_date"])
        fee_percent = Decimal(str(data.get("service_fee_percent", "9")))
        deposit = Decimal(str(data["security_deposit_ghs"]))
        rent = Decimal(str(data["monthly_rent_ghs"]))
        if end <= start or rent <= 0 or deposit < 0 or not Decimal("8") <= fee_percent <= Decimal("10"):
            raise ValueError
    except (KeyError, ValueError, InvalidOperation):
        return {"error": "Valid property, dates, rent, deposit, and service fee (0-30%) are required"}, 400

    property_ = db.session.get(Property, property_id)
    if property_ is None or not property_.is_available or not property_.is_verified:
        return {"error": "Property is not currently available for booking"}, 409
    if rent != property_.monthly_rent_ghs:
        return {"error": "Monthly rent must match the verified property listing"}, 422
    master = db.session.scalar(
        select(MasterLease).where(
            MasterLease.property_id == property_id,
            MasterLease.status == LeaseStatus.ACTIVE,
            MasterLease.start_date <= start,
            MasterLease.end_date >= end,
        )
    )
    if master is None:
        return {"error": "Property does not have an active master lease covering the requested term"}, 409
    tenant_id = int(get_jwt_identity())
    underwriting = db.session.scalar(
        select(UnderwritingProfile).where(UnderwritingProfile.tenant_id == tenant_id)
    )
    if underwriting is None:
        return {"error": "Complete an affordability assessment before booking"}, 409
    monthly_total = rent * (Decimal("1") + fee_percent / Decimal("100"))
    if monthly_total > underwriting.max_monthly_installment_ghs:
        return {
            "error": "Monthly installment exceeds your assessed affordability limit",
            "monthly_total_ghs": str(monthly_total),
            "maximum_ghs": str(underwriting.max_monthly_installment_ghs),
        }, 422
    lease = TenantLease(
        property_id=property_id,
        tenant_id=tenant_id,
        monthly_rent_ghs=rent,
        service_fee_percent=fee_percent,
        security_deposit_ghs=deposit,
        momo_provider=data.get("momo_provider"),
        start_date=start,
        end_date=end,
    )
    db.session.add(lease)
    property_.is_available = False
    db.session.commit()
    return {
        "tenant_lease": {
            "id": lease.id,
            "property_id": lease.property_id,
            "monthly_rent_ghs": float(lease.monthly_rent_ghs),
            "service_fee_percent": float(lease.service_fee_percent),
            "monthly_total_ghs": float(lease.monthly_total_ghs),
            "security_deposit_ghs": float(lease.security_deposit_ghs),
            "start_date": lease.start_date.isoformat(),
            "end_date": lease.end_date.isoformat(),
            "status": lease.status.value,
        }
    }, 201
