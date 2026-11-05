from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, request
from flask_jwt_extended import get_jwt, get_jwt_identity
from sqlalchemy import select

from app.api.decorators import roles_required
from app.extensions import db
from app.models import Landlord, LeaseStatus, MasterLease, Property, Role

bp = Blueprint("master_leases", __name__)


@bp.post("/onboard")
@roles_required(Role.FIELD_AGENT, Role.ADMIN)
def onboard_property_and_lease() -> tuple[dict[str, object], int]:
    data = request.get_json(silent=True) or {}
    try:
        start = date.fromisoformat(data["start_date"])
        end = date.fromisoformat(data["end_date"])
        rent = Decimal(str(data["monthly_rent_ghs"]))
        advance = Decimal(str(data["advance_paid_ghs"]))
        discount = Decimal(str(data["discount_percent"]))
        bedrooms = int(data.get("bedrooms", 1))
        bathrooms = int(data.get("bathrooms", 1))
        required = ("title", "region", "neighborhood", "address", "landlord_name")
        if any(not str(data.get(field, "")).strip() for field in required):
            raise ValueError
        if end <= start or rent <= 0 or advance <= 0 or not Decimal("5") <= discount <= Decimal("10"):
            raise ValueError
        if bedrooms < 0 or bathrooms < 0:
            raise ValueError
    except (KeyError, ValueError, InvalidOperation, TypeError):
        return {"error": "Valid property details, landlord name, lease dates, rent, advance, and discount are required"}, 400

    agent_id = int(get_jwt_identity())
    landlord = Landlord(
        full_name=str(data["landlord_name"]).strip(),
        phone=data.get("landlord_phone"),
        notes=data.get("landlord_notes"),
        created_by_id=agent_id,
    )
    property_ = Property(
        title=str(data["title"]).strip(),
        description=str(data.get("description", "")),
        region=str(data["region"]).strip(),
        neighborhood=str(data["neighborhood"]).strip(),
        address=str(data["address"]).strip(),
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        amenities=data.get("amenities", []),
        monthly_rent_ghs=rent,
        available_from=start,
        is_verified=bool(data.get("contract_document_url")),
        is_available=bool(data.get("contract_document_url")),
        agent_id=agent_id,
    )
    db.session.add_all([landlord, property_])
    db.session.flush()
    lease = MasterLease(
        property_id=property_.id,
        landlord_id=landlord.id,
        advance_paid_ghs=advance,
        discount_percent=discount,
        start_date=start,
        end_date=end,
        contract_document_url=data.get("contract_document_url"),
        status=LeaseStatus.ACTIVE if data.get("contract_document_url") else LeaseStatus.DRAFT,
        created_by_id=agent_id,
    )
    db.session.add(lease)
    db.session.commit()
    return {
        "property": property_.to_dict(),
        "master_lease": {
            "id": lease.id,
            "advance_paid_ghs": float(lease.advance_paid_ghs),
            "discount_percent": float(lease.discount_percent),
            "start_date": lease.start_date.isoformat(),
            "end_date": lease.end_date.isoformat(),
            "status": lease.status.value,
        },
    }, 201


@bp.post("")
@roles_required(Role.FIELD_AGENT, Role.ADMIN)
def create_master_lease() -> tuple[dict[str, object], int]:
    data = request.get_json(silent=True) or {}
    try:
        property_ = db.session.get(Property, int(data["property_id"]))
        landlord_name = str(data["landlord_name"]).strip()
        start = date.fromisoformat(data["start_date"])
        end = date.fromisoformat(data["end_date"])
        advance = Decimal(str(data["advance_paid_ghs"]))
        discount = Decimal(str(data["discount_percent"]))
        if not landlord_name or end <= start or advance <= 0 or not Decimal("5") <= discount <= Decimal("10"):
            raise ValueError
    except (KeyError, ValueError, InvalidOperation, TypeError):
        return {"error": "Valid property, landlord, dates, positive advance, and 0-100% discount are required"}, 400
    if property_ is None:
        return {"error": "Property not found"}, 404
    if get_jwt().get("role") != Role.ADMIN.value and property_.agent_id != int(get_jwt_identity()):
        return {"error": "Property not found"}, 404
    if db.session.scalar(select(MasterLease.id).where(MasterLease.property_id == property_.id)):
        return {"error": "This property already has a master lease"}, 409

    landlord = Landlord(
        full_name=landlord_name,
        phone=data.get("landlord_phone"),
        notes=data.get("landlord_notes"),
        created_by_id=int(get_jwt_identity()),
    )
    db.session.add(landlord)
    db.session.flush()
    lease = MasterLease(
        property_id=property_.id,
        landlord_id=landlord.id,
        advance_paid_ghs=advance,
        discount_percent=discount,
        start_date=start,
        end_date=end,
        contract_document_url=data.get("contract_document_url"),
        status=LeaseStatus.ACTIVE if data.get("contract_document_url") else LeaseStatus.DRAFT,
        created_by_id=int(get_jwt_identity()),
    )
    property_.is_available = lease.status == LeaseStatus.ACTIVE
    property_.is_verified = lease.status == LeaseStatus.ACTIVE
    db.session.add(lease)
    db.session.commit()
    return {
        "master_lease": {
            "id": lease.id,
            "property_id": lease.property_id,
            "landlord_id": lease.landlord_id,
            "advance_paid_ghs": float(lease.advance_paid_ghs),
            "discount_percent": float(lease.discount_percent),
            "start_date": lease.start_date.isoformat(),
            "end_date": lease.end_date.isoformat(),
            "status": lease.status.value,
        }
    }, 201
