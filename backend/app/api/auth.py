from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Role, User

bp = Blueprint("auth", __name__)


@bp.post("/register")
def register() -> tuple[dict[str, object], int]:
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password")
    full_name = str(data.get("full_name", "")).strip()
    if not full_name or not isinstance(password, str) or len(password) < 12:
        return {"error": "Full name and a password of at least 12 characters are required"}, 400
    try:
        email = validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError:
        return {"error": "A valid email address is required"}, 400
    phone = str(data["phone"]).strip() or None if data.get("phone") else None
    existing_user = select(User.id).where(User.email == email)
    if phone:
        existing_user = select(User.id).where(or_(User.email == email, User.phone == phone))
    if db.session.scalar(existing_user):
        return {"error": "An account with this email or phone already exists"}, 409

    user = User(email=email, full_name=full_name, phone=phone, role=Role.TENANT)
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "An account with this email or phone already exists"}, 409
    return {"user": user.to_dict()}, 201


@bp.post("/login")
def login() -> tuple[dict[str, object], int]:
    data = request.get_json(silent=True) or {}
    user = db.session.scalar(select(User).where(User.email == str(data.get("email", "")).lower()))
    if user is None or not user.is_active or not user.check_password(str(data.get("password", ""))):
        return {"error": "Invalid email or password"}, 401
    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role.value})
    return {"access_token": token, "user": user.to_dict()}, 200


@bp.get("/me")
@jwt_required()
def me() -> tuple[dict[str, object], int]:
    user = db.session.get(User, int(get_jwt_identity()))
    if user is None or not user.is_active:
        return {"error": "Account not found or inactive"}, 404
    return jsonify(user=user.to_dict()), 200
