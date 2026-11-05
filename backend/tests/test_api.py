from decimal import Decimal

from flask_jwt_extended import create_access_token
from sqlalchemy import select

from app.api.underwriting import assess_profile
from app.extensions import db
from app.models import Landlord, Role, User


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_public_registration_cannot_escalate_role(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "tenant@example.com",
            "full_name": "A Ghanaian Tenant",
            "password": "a-very-long-test-password",
            "role": "ADMIN",
        },
    )
    assert response.status_code == 201
    assert response.json["user"]["role"] == "TENANT"


def test_property_search_rejects_bad_price(client):
    response = client.get("/api/properties?min_price=not-a-number")
    assert response.status_code == 400
    assert "Price filters" in response.json["error"]


def test_underwriting_returns_installment_cap():
    score, rating, limit = assess_profile(
        Decimal("4000"), Decimal("3600"), employer_verified=True, salary_deduction=True
    )
    assert score == 95
    assert rating == "LOW"
    assert limit == Decimal("1400.00")


def test_field_agent_onboarding_creates_landlord_property_and_lease(app, client):
    with app.app_context():
        agent = User(email="agent@example.com", full_name="Field Agent", role=Role.FIELD_AGENT)
        agent.set_password("a-long-test-password")
        db.session.add(agent)
        db.session.commit()
        token = create_access_token(
            identity=str(agent.id), additional_claims={"role": Role.FIELD_AGENT.value}
        )

    response = client.post(
        "/api/master-leases/onboard",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Accra Garden Flat",
            "region": "Greater Accra",
            "neighborhood": "East Legon",
            "address": "Accra",
            "landlord_name": "Managed Landlord",
            "monthly_rent_ghs": "3000",
            "advance_paid_ghs": "68400",
            "discount_percent": "5",
            "start_date": "2026-12-01",
            "end_date": "2028-11-30",
            "contract_document_url": "https://documents.example/lease.pdf",
        },
    )

    assert response.status_code == 201
    assert response.json["property"]["is_available"] is True
    assert response.json["master_lease"]["status"] == "ACTIVE"
    with app.app_context():
        assert db.session.scalar(select(Landlord.id)) is not None


def test_tenant_cannot_use_field_agent_property_route(app, client):
    with app.app_context():
        tenant = User(email="tenant@example.com", full_name="Tenant", role=Role.TENANT)
        tenant.set_password("a-long-test-password")
        db.session.add(tenant)
        db.session.commit()
        token = create_access_token(
            identity=str(tenant.id), additional_claims={"role": Role.TENANT.value}
        )

    response = client.post(
        "/api/properties",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "No access",
            "region": "Greater Accra",
            "neighborhood": "Tema",
            "address": "Tema",
            "monthly_rent_ghs": 3000,
        },
    )
    assert response.status_code == 403
