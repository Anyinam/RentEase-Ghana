from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class Role(StrEnum):
    TENANT = "TENANT"
    FIELD_AGENT = "FIELD_AGENT"
    ADMIN = "ADMIN"
    FINANCIAL_PARTNER = "FINANCIAL_PARTNER"


class LeaseStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"
    TERMINATED = "TERMINATED"


class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(160), nullable=False)
    phone = db.Column(db.String(32), nullable=True, unique=True)
    role = db.Column(db.Enum(Role, native_enum=False), nullable=False, default=Role.TENANT)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "phone": self.phone,
            "role": self.role.value,
        }


class Landlord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(160), nullable=False)
    phone = db.Column(db.String(32), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    region = db.Column(db.String(80), nullable=False, index=True)
    neighborhood = db.Column(db.String(100), nullable=False, index=True)
    address = db.Column(db.String(255), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False, default=1)
    bathrooms = db.Column(db.Integer, nullable=False, default=1)
    amenities = db.Column(db.JSON, nullable=False, default=list)
    monthly_rent_ghs = db.Column(db.Numeric(12, 2), nullable=False)
    available_from = db.Column(db.Date, nullable=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    is_available = db.Column(db.Boolean, nullable=False, default=False, index=True)
    has_virtual_tour = db.Column(db.Boolean, nullable=False, default=False)
    agent_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    media = db.relationship("PropertyMedia", back_populates="property", cascade="all, delete-orphan")

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "region": self.region,
            "neighborhood": self.neighborhood,
            "address": self.address,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "amenities": self.amenities,
            "monthly_rent_ghs": float(self.monthly_rent_ghs),
            "available_from": self.available_from.isoformat() if self.available_from else None,
            "is_verified": self.is_verified,
            "is_available": self.is_available,
            "has_virtual_tour": self.has_virtual_tour,
            "media": [item.to_dict() for item in self.media],
        }


class PropertyMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("property.id"), nullable=False, index=True)
    url = db.Column(db.String(1024), nullable=False)
    media_type = db.Column(db.String(32), nullable=False, default="IMAGE")
    mime_type = db.Column(db.String(100), nullable=False)
    is_primary = db.Column(db.Boolean, nullable=False, default=False)
    property = db.relationship("Property", back_populates="media")

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "url": self.url,
            "media_type": self.media_type,
            "mime_type": self.mime_type,
            "is_primary": self.is_primary,
        }


class MasterLease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("property.id"), nullable=False, unique=True)
    landlord_id = db.Column(db.Integer, db.ForeignKey("landlord.id"), nullable=False)
    advance_paid_ghs = db.Column(db.Numeric(12, 2), nullable=False)
    discount_percent = db.Column(db.Numeric(5, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    contract_document_url = db.Column(db.String(1024), nullable=True)
    status = db.Column(db.Enum(LeaseStatus, native_enum=False), nullable=False, default=LeaseStatus.DRAFT)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))


class TenantLease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("property.id"), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    monthly_rent_ghs = db.Column(db.Numeric(12, 2), nullable=False)
    service_fee_percent = db.Column(db.Numeric(5, 2), nullable=False, default=Decimal("9.00"))
    security_deposit_ghs = db.Column(db.Numeric(12, 2), nullable=False)
    momo_provider = db.Column(db.String(32), nullable=True)
    momo_authorization_code = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(LeaseStatus, native_enum=False), nullable=False, default=LeaseStatus.DRAFT)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    @property
    def monthly_total_ghs(self) -> Decimal:
        return self.monthly_rent_ghs * (Decimal("1") + self.service_fee_percent / Decimal("100"))


class UnderwritingProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    monthly_income_ghs = db.Column(db.Numeric(12, 2), nullable=False)
    income_sources = db.Column(db.JSON, nullable=False, default=list)
    momo_monthly_inflow_ghs = db.Column(db.Numeric(12, 2), nullable=False)
    employer_verified = db.Column(db.Boolean, nullable=False, default=False)
    salary_deduction_authorized = db.Column(db.Boolean, nullable=False, default=False)
    risk_score = db.Column(db.Integer, nullable=False)
    risk_rating = db.Column(db.String(20), nullable=False)
    max_monthly_installment_ghs = db.Column(db.Numeric(12, 2), nullable=False)
    reviewed_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))


class PaymentTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_lease_id = db.Column(db.Integer, db.ForeignKey("tenant_lease.id"), nullable=False, index=True)
    amount_ghs = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="GHS")
    provider = db.Column(db.String(32), nullable=False)
    provider_reference = db.Column(db.String(120), unique=True, nullable=False, index=True)
    status = db.Column(db.Enum(PaymentStatus, native_enum=False), nullable=False, default=PaymentStatus.PENDING)
    payment_type = db.Column(db.String(40), nullable=False, default="MONTHLY_RENT")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))


class LedgerEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_group_id = db.Column(db.String(36), nullable=False, index=True)
    account_code = db.Column(db.String(48), nullable=False)
    debit_ghs = db.Column(db.Numeric(14, 2), nullable=False, default=Decimal("0"))
    credit_ghs = db.Column(db.Numeric(14, 2), nullable=False, default=Decimal("0"))
    description = db.Column(db.String(255), nullable=False)
    payment_transaction_id = db.Column(db.Integer, db.ForeignKey("payment_transaction.id"), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    @staticmethod
    def post_pair(
        transaction_group_id: str,
        debit_account: str,
        credit_account: str,
        amount: Decimal,
        description: str,
        payment_transaction_id: int | None = None,
    ) -> None:
        if amount <= 0:
            raise ValueError("Ledger amount must be positive")
        db.session.add_all(
            [
                LedgerEntry(
                    transaction_group_id=transaction_group_id,
                    account_code=debit_account,
                    debit_ghs=amount,
                    description=description,
                    payment_transaction_id=payment_transaction_id,
                ),
                LedgerEntry(
                    transaction_group_id=transaction_group_id,
                    account_code=credit_account,
                    credit_ghs=amount,
                    description=description,
                    payment_transaction_id=payment_transaction_id,
                ),
            ]
        )
