from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request, url_for
from flask_jwt_extended import get_jwt, get_jwt_identity
from sqlalchemy import or_, select

from app.api.decorators import roles_required
from app.extensions import db
from app.models import Property, PropertyMedia, Role

bp = Blueprint("properties", __name__)
IMAGE_MIMES = {"image/jpeg", "image/png", "image/webp"}
PANO_MIMES = {"image/jpeg", "image/png"}
MAX_MEDIA_BYTES = 16 * 1024 * 1024


@bp.get("")
def search_properties() -> tuple[dict[str, object], int]:
    query = select(Property).where(Property.is_available.is_(True))
    region = request.args.get("region", "").strip()
    neighborhood = request.args.get("neighborhood", "").strip()
    search = request.args.get("q", "").strip()
    if region:
        query = query.where(Property.region.ilike(f"%{region}%"))
    if neighborhood:
        query = query.where(Property.neighborhood.ilike(f"%{neighborhood}%"))
    if search:
        query = query.where(
            or_(
                Property.region.ilike(f"%{search}%"),
                Property.neighborhood.ilike(f"%{search}%"),
            )
        )
    if request.args.get("virtual_tour", "").lower() == "true":
        query = query.where(Property.has_virtual_tour.is_(True))
    if request.args.get("available_from"):
        try:
            available_from = date.fromisoformat(request.args["available_from"])
        except ValueError:
            return {"error": "available_from must use YYYY-MM-DD"}, 400
        query = query.where(
            (Property.available_from.is_(None)) | (Property.available_from <= available_from)
        )
    try:
        if request.args.get("min_price"):
            query = query.where(Property.monthly_rent_ghs >= Decimal(request.args["min_price"]))
        if request.args.get("max_price"):
            query = query.where(Property.monthly_rent_ghs <= Decimal(request.args["max_price"]))
    except InvalidOperation:
        return {"error": "Price filters must be valid numbers"}, 400
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 12, type=int), 1), 50)
    pagination = db.paginate(query.order_by(Property.created_at.desc()), page=page, per_page=per_page)
    return {
        "items": [property_.to_dict() for property_ in pagination.items],
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }, 200


@bp.get("/<int:property_id>")
def get_property(property_id: int) -> tuple[dict[str, object], int]:
    property_ = db.session.get(Property, property_id)
    if property_ is None or not property_.is_available:
        return {"error": "Property not found"}, 404
    return {"property": property_.to_dict()}, 200


@bp.post("")
@roles_required(Role.FIELD_AGENT, Role.ADMIN)
def create_property() -> tuple[dict[str, object], int]:
    data = request.get_json(silent=True) or {}
    required = ("title", "region", "neighborhood", "address", "monthly_rent_ghs")
    if any(not str(data.get(field, "")).strip() for field in required):
        return {"error": "title, region, neighborhood, address, and monthly_rent_ghs are required"}, 400
    try:
        rent = Decimal(str(data["monthly_rent_ghs"]))
        bedrooms = int(data.get("bedrooms", 1))
        bathrooms = int(data.get("bathrooms", 1))
        available_from = date.fromisoformat(data["available_from"]) if data.get("available_from") else None
    except (InvalidOperation, ValueError):
        return {"error": "Rent and room counts must be valid numbers and available_from must use YYYY-MM-DD"}, 400
    if rent <= 0 or bedrooms < 0 or bathrooms < 0:
        return {"error": "Rent must be positive and room counts cannot be negative"}, 400
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
        available_from=available_from,
        is_available=False,
        agent_id=int(get_jwt_identity()),
    )
    db.session.add(property_)
    db.session.commit()
    return {"property": property_.to_dict()}, 201


@bp.post("/<int:property_id>/media")
@roles_required(Role.FIELD_AGENT, Role.ADMIN)
def upload_media(property_id: int) -> tuple[dict[str, object], int]:
    property_ = db.session.get(Property, property_id)
    if property_ is None:
        return {"error": "Property not found"}, 404
    if get_jwt().get("role") != Role.ADMIN.value and property_.agent_id != int(get_jwt_identity()):
        return {"error": "Property not found"}, 404
    upload = request.files.get("file")
    media_type = request.form.get("media_type", "IMAGE").upper()
    if upload is None or not upload.filename:
        return {"error": "A media file is required"}, 400
    allowed_mimes = PANO_MIMES if media_type == "PANORAMA" else IMAGE_MIMES
    if media_type not in {"IMAGE", "PANORAMA"} or upload.mimetype not in allowed_mimes:
        return {"error": "Unsupported media type or image format"}, 415
    content = upload.stream.read(MAX_MEDIA_BYTES + 1)
    if len(content) > MAX_MEDIA_BYTES:
        return {"error": "Image exceeds the 16 MB limit"}, 413
    if not content.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"RIFF")):
        return {"error": "The uploaded file does not match an allowed image format"}, 415
    extension = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[upload.mimetype]
    target_dir = Path(current_app.config["UPLOAD_FOLDER"]) / str(property_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    (target_dir / filename).write_bytes(content)
    media = PropertyMedia(
        property_id=property_id,
        url=url_for("static_media", property_id=property_id, filename=filename),
        media_type=media_type,
        mime_type=upload.mimetype,
        is_primary=request.form.get("is_primary") == "true",
    )
    db.session.add(media)
    if media_type == "PANORAMA":
        property_.has_virtual_tour = True
    db.session.commit()
    return {"media": media.to_dict()}, 201


def register_media_route(app: object) -> None:
    from flask import send_from_directory

    app.add_url_rule(
        "/media/<int:property_id>/<path:filename>",
        endpoint="static_media",
        view_func=lambda property_id, filename: send_from_directory(
            str(Path(current_app.config["UPLOAD_FOLDER"]) / str(property_id)), filename
        ),
    )
