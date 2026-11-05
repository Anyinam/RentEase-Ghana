# RentEase Ghana

RentEase is a Ghana-focused managed-subleasing and rent-flexibility platform scaffold. The platform leases homes from landlords through field-agent-managed master leases, then offers verified homes to tenants with a monthly payment option. Landlords are operational records, not web users.

> **Financial services status:** This repository is a development scaffold, not a live payment or credit product. Payment checkout, verified recurring MoMo mandates, Paystack/Hubtel callbacks, SMS delivery, identity verification, credit bureau integrations, production file storage, and financial reconciliation require provider contracts, secrets, signed legal terms, and implementation/validation before any live use. The API intentionally fails closed when payment configuration is missing and does not request/store a MoMo PIN.

## Architecture

- **API:** Python 3.11+ Flask application factory, SQLAlchemy, Flask-Migrate/Alembic, JWT, and role-protected blueprints.
- **Web:** React 18, Vite, TypeScript, Tailwind CSS, TanStack Query, Lucide icons, and Pannellum equirectangular panorama viewer.
- **Data and async:** PostgreSQL 15, Redis, and Celery worker.
- **Ledger:** Double-entry posting primitive (`LedgerEntry.post_pair`) for balanced debit/credit entries. Journal posting/reconciliation workflows must be connected to audited payment and payout processes before launch.
- **Roles:** `TENANT`, `FIELD_AGENT`, `ADMIN`, and `FINANCIAL_PARTNER`. Public registration always creates a `TENANT`; privileged accounts need a controlled provisioning process.

## Repository layout

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── decorators.py
│   │   │   ├── master_leases.py
│   │   │   ├── payments.py
│   │   │   ├── properties.py
│   │   │   ├── tenant_leases.py
│   │   │   └── underwriting.py
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── models.py            # users, property/media, leases, payments, ledger
│   │   ├── tasks.py             # Celery task entry points (provider work is gated)
│   │   └── celery.py
│   ├── migrations/versions/      # Alembic initial schema
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── wsgi.py
├── frontend/
│   ├── src/components/
│   │   ├── CheckoutDrawer.tsx
│   │   ├── FieldAgentOnboarding.tsx
│   │   ├── PanoramaTour.tsx
│   │   ├── PropertyCard.tsx
│   │   └── RnplSimulator.tsx
│   ├── src/App.tsx
│   ├── src/main.tsx
│   ├── Dockerfile
│   └── package.json
├── docker/
│   ├── postgres/                # PostgreSQL multi-stage image and config
│   └── redis/                   # Redis multi-stage image and config
├── .env.example
└── docker-compose.yml
```

## Run locally with Docker

```sh
cp .env.example .env
# Replace SECRET_KEY and JWT_SECRET_KEY before exposing any service.
docker compose up --build
```

- Web: <http://localhost:8080>
- API health: <http://localhost:5000/health>
- Property API: <http://localhost:5000/api/properties>

The API container runs `flask db upgrade` before Gunicorn starts. For local development without Docker, install `backend/requirements-dev.txt`, set `DATABASE_URL` (SQLite is the default for local smoke tests), then run `flask --app wsgi db upgrade` and `flask --app wsgi run`. Start the frontend separately with `cd frontend && npm install && npm run dev`.

## API outline

| Route | Access | Purpose |
|---|---|---|
| `POST /api/auth/register` | Public; tenant only | Create a tenant account |
| `POST /api/auth/login` | Public | Issue an access token |
| `GET /api/auth/me` | Authenticated | Current account |
| `GET /api/properties` | Public | Paginated region/neighborhood/date/price/tour search |
| `POST /api/properties` | Field agent/admin | Add an inspected property |
| `POST /api/properties/{id}/media` | Field agent/admin | Upload a bounded image or panorama |
| `POST /api/master-leases/onboard` | Field agent/admin | Create landlord, property and draft/active master lease |
| `POST /api/underwriting/assess` | Tenant/admin | Store a preliminary affordability estimate |
| `POST /api/tenant-leases` | Tenant/admin | Create a sublease within affordability and master-lease limits |
| `POST /api/payments/checkout` | Tenant | Payment initialization (provider adapter is not yet enabled) |

Use the Authorization header format `Bearer <access_token>`. The underwriting rules are a transparent starter heuristic, not a validated credit model, and must not be used as a sole or adverse eligibility decision. Avoid collecting raw MoMo statements or payment credentials until consent, access controls, retention, encryption, and provider requirements are implemented.

Create an operator from a trusted shell with `flask --app wsgi create-operator --email agent@example.com --name "Field Agent" --role FIELD_AGENT`; the command prompts for a temporary password. Public registration cannot create privileged roles.

## Development checks

```sh
cd backend && python -m pytest
cd frontend && npm run build
```

## Production readiness checklist

- Configure secure secrets, TLS, a managed PostgreSQL/Redis service, backups, monitoring and rate limits.
- Replace local media storage with private object storage, malware scanning, MIME/content validation and signed URLs.
- Implement and test signed Paystack/Hubtel webhook verification, idempotency, charge retries, reconciliation, refund paths, and an encrypted recurring-payment mandate store.
- Provision privileged roles out-of-band; implement audit logging, session revocation, MFA for operators, and tenant data access controls.
- Review Ghana Data Protection Act obligations, consent/retention, tenancy and master-lease legal templates, payment-provider rules, and consumer disclosures with local counsel.
- Build an audited ledger posting service and prove journal balance/reconciliation invariants before handling real funds.
