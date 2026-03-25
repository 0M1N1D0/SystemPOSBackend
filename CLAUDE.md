# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SystemPOS Backend** — REST API backend for a restaurant Point-of-Sale system. Written in **Python**. The implementation has not started yet; only database design documentation exists so far.

## Architecture: Clean Architecture

All implementation must follow Clean Architecture with these four layers (inner layers must never depend on outer layers):

```
Domain Layer        → Entities and business rules. Zero external dependencies.
Application Layer   → Use cases that orchestrate domain logic.
Infrastructure Layer → Database, external APIs, framework adapters.
Presentation Layer  → HTTP controllers/routes (the outermost layer).
```

Enforce SOLID principles throughout. Dependency injection flows inward.

## Database Design

The relational schema (see `documentation/database_design.md`) has 14 entities. All column types use PostgreSQL nomenclature.

- **Branches:** `BRANCH` (name, address, phone, is_active) — supports multi-branch chains
- **Auth/Users:** `USER` (dual auth: 6-digit PIN for POS terminals, email+password for web dashboard; `password_hash` and `email` are nullable for PIN-only users; `is_active` for soft delete; optional `branch_id FK`), `ROLE` (Admin/Manager/Waiter)
- **Catalog:** `CATEGORY` (optional sort_order), `PRODUCT` (base_price as NUMERIC(12,4), is_available, optional sort_order, optional tax_rate_id FK), `MODIFIER` (extra_price NUMERIC(12,4), default 0.0)
- **Tax:** `TAX_RATE` (name, rate NUMERIC(5,4) 0.0–1.0, is_default, is_active) — uniqueness of is_default=True enforced by partial unique index
- **Operations:** `RESTAURANT_TABLE` (branch_id FK NOT NULL, status: FREE/OCCUPIED/RESERVED), `ORDER` (subtotal/taxes/tip/discount/total_amount as NUMERIC(12,4), status: OPEN/PAID/CANCELLED, payment_method nullable, updated_at), `ORDER_TABLE` (join table, PK composite on order_id+table_id), `ORDER_ITEM` (copies unit_price and applied_tax_rate at time of order; status for KDS: PENDING/IN_PREPARATION/READY/DELIVERED/CANCELLED), `ORDER_ITEM_MODIFIER` (copies applied_extra_price at time of order)
- **Reservations:** `RESERVATION` (branch_id FK NOT NULL denormalized for branch-level queries, created_by_user_id FK NOT NULL, order_id FK nullable — linked when guest arrives; guest_name/phone/party_size; scheduled_at TIMESTAMPTZ, duration_minutes INTEGER DEFAULT 90; status: CONFIRMED/SEATED/CANCELLED/NO_SHOW), `RESERVATION_TABLE` (join table, PK composite on reservation_id+table_id — supports reserving multiple joined tables for large groups; mirrors order_table pattern)
- **Config:** `SYSTEM_CONFIG` (key VARCHAR(100) PK, value TEXT) — business settings: suggested tips, billing info, reservation threshold
- **Audit:** `AUDIT_LOG` (user_id, action, optional JSONB details, timestamp)

Key design decisions:
- PINs and passwords are hashed with bcrypt (`CHAR(60)`), never stored in plaintext
- `password_hash` and `email` are nullable — PIN-only users (e.g. waiters) need neither
- `is_active` on `USER` enables soft delete without breaking FK references in `ORDER` / `AUDIT_LOG`
- Monetary fields use `NUMERIC(12,4)`, tax rates use `NUMERIC(5,4)` — never `FLOAT` (floating-point precision errors are unacceptable for financial data)
- `unit_price` and `applied_tax_rate` on `ORDER_ITEM` snapshot values at order time (not FKs to current catalog)
- `applied_extra_price` on `ORDER_ITEM_MODIFIER` snapshots the modifier price at order time
- Tax rate resolution order: product's explicit `tax_rate_id` → fallback to `TAX_RATE` with `is_default=True`
- `ORDER.total_amount` = `subtotal + taxes + tip - discount`
- `ORDER.taxes` = sum of `(unit_price × quantity × applied_tax_rate)` across all ORDER_ITEMs
- `ORDER.discount` stores the result of `DISCOUNT_APPLIED` audit events
- `ORDER_TABLE` has composite PK `(order_id, table_id)` — no separate UUID needed
- `RESERVATION_TABLE` has composite PK `(reservation_id, table_id)` — same pattern as `ORDER_TABLE`; allows reserving multiple joined tables for large parties
- Reservation lifecycle: `CONFIRMED` → `SEATED` (guest arrived, order opened) / `CANCELLED` / `NO_SHOW`; terminal states validated in domain entity
- `RESTAURANT_TABLE.status` is managed by use cases, not triggers: use case sets `RESERVED` when a `CONFIRMED` reservation is within the threshold (`reservation_upcoming_threshold_minutes` in `SYSTEM_CONFIG`)
- Overlap validation (two reservations for the same table in the same time slot) is a domain rule enforced in the use case, not a DB constraint
- `RESERVATION.branch_id` is denormalized (also reachable via `reservation_table → restaurant_table`) for efficient branch-level queries without extra JOINs
- `AUDIT_LOG.details` is `JSONB` (binary, indexable, queryable via `details->>'field'`)
- `RESTAURANT_TABLE` avoids SQL reserved keyword `TABLE`
- `RESTAURANT_TABLE.branch_id` is NOT NULL — every table belongs to a branch
- User name fields use `given_name`, `paternal_surname`, `maternal_surname` for clarity
- UUIDs generated in Python (`uuid.uuid4()`), not by PostgreSQL — required by Clean Architecture (entity ID known before INSERT)
- `TAX_RATE.is_default` uniqueness enforced by: `CREATE UNIQUE INDEX ON tax_rate (is_default) WHERE is_default = TRUE`

## Development Setup

Python virtual environment (use `.venv/`):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Base de datos local (PostgreSQL)

Las credenciales de conexión están en `.env` (ver `.env.example` como referencia). No commitear `.env`.

`psql` disponible en:
```
/Applications/pgAdmin 4.app/Contents/SharedSupport/psql
```

Ejemplo de uso (carga credenciales desde `.env`):
```bash
export $(grep -v '^#' .env | xargs)
PGPASSWORD=$DB_PASSWORD /Applications/pgAdmin\ 4.app/Contents/SharedSupport/psql \
  -h $DB_HOST -U $DB_USER -d $DB_NAME -p $DB_PORT
```

## Commands

These will apply once the project is set up (adapt as the stack is chosen):

```bash
# Run the development server
python -m uvicorn app.main:app --reload       # if FastAPI
# or
flask run                                      # if Flask

# Run all tests
pytest

# Run a single test file
pytest tests/path/to/test_file.py

# Run a single test
pytest tests/path/to/test_file.py::test_name

# Lint
flake8 .
# or
ruff check .
```

## Language Convention

- **Code:** English (variable names, function names, comments in code)
- **Documentation:** Spanish (docstrings, markdown docs, commit messages may be Spanish)
