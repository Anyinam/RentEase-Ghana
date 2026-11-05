from decimal import Decimal, InvalidOperation

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import select

from app.api.decorators import roles_required
from app.extensions import db
from app.models import Role, UnderwritingProfile

bp = Blueprint("underwriting", __name__)


def assess_profile(income: Decimal, momo_inflow: Decimal, employer_verified: bool, salary_deduction: bool) -> tuple[int, str, Decimal]:
    if income <= 0 or momo_inflow < 0:
        raise ValueError("Income must be positive and MoMo inflows cannot be negative")
    score = 55
    score += 15 if employer_verified else 0
    score += 10 if salary_deduction else 0
    if momo_inflow >= income * Decimal("0.8"):
        score += 15
    elif momo_inflow >= income * Decimal("0.5"):
        score += 8
    score = min(score, 100)
    rating = "LOW" if score >= 75 else "MEDIUM" if score >= 60 else "HIGH"
    limit = income * (Decimal("0.35") if score >= 75 else Decimal("0.25") if score >= 60 else Decimal("0.15"))
    return score, rating, limit.quantize(Decimal("0.01"))


@bp.post("/assess")
@roles_required(Role.TENANT, Role.ADMIN)
def assess() -> tuple[dict[str, object], int]:
    data = request.get_json(silent=True) or {}
    if any(
        key in data and not isinstance(data[key], bool)
        for key in ("employer_verified", "salary_deduction_authorized")
    ):
        return {"error": "Employer verification and salary deduction must be boolean values"}, 400
    if "income_sources" in data and (
        not isinstance(data["income_sources"], list)
        or any(not isinstance(source, str) or not source.strip() for source in data["income_sources"])
    ):
        return {"error": "income_sources must be a list of non-empty strings"}, 400
    try:
        income = Decimal(str(data["monthly_income_ghs"]))
        inflow = Decimal(str(data["momo_monthly_inflow_ghs"]))
        score, rating, limit = assess_profile(
            income, inflow, bool(data.get("employer_verified")), bool(data.get("salary_deduction_authorized"))
        )
    except (KeyError, InvalidOperation, ValueError):
        return {"error": "Valid monthly_income_ghs and momo_monthly_inflow_ghs are required"}, 400
    tenant_id = int(get_jwt_identity())
    profile = db.session.scalar(select(UnderwritingProfile).where(UnderwritingProfile.tenant_id == tenant_id))
    values = {
        "monthly_income_ghs": income,
        "income_sources": data.get("income_sources", []),
        "momo_monthly_inflow_ghs": inflow,
        "employer_verified": bool(data.get("employer_verified")),
        "salary_deduction_authorized": bool(data.get("salary_deduction_authorized")),
        "risk_score": score,
        "risk_rating": rating,
        "max_monthly_installment_ghs": limit,
    }
    if profile is None:
        profile = UnderwritingProfile(tenant_id=tenant_id, **values)
        db.session.add(profile)
    else:
        for key, value in values.items():
            setattr(profile, key, value)
    db.session.commit()
    return {
        "risk_score": score,
        "risk_rating": rating,
        "max_monthly_installment_ghs": float(limit),
        "disclaimer": "Preliminary affordability estimate; not a credit decision. Verify statements and consent before approval.",
    }, 200


@bp.get("/me")
@roles_required(Role.TENANT, Role.ADMIN)
def my_profile() -> tuple[dict[str, object], int]:
    profile = db.session.scalar(
        select(UnderwritingProfile).where(UnderwritingProfile.tenant_id == int(get_jwt_identity()))
    )
    if profile is None:
        return {"error": "No underwriting profile found"}, 404
    return {
        "risk_score": profile.risk_score,
        "risk_rating": profile.risk_rating,
        "max_monthly_installment_ghs": float(profile.max_monthly_installment_ghs),
    }, 200
