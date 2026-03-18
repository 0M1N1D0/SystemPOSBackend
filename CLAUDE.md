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

The relational schema (see `documentation/database_design.md`) has 10 entities with UUIDs as PKs:

- **Auth/Users:** `USER` (dual auth: 6-digit PIN for POS terminals, email+password for web dashboard; `password_hash` is nullable for PIN-only users), `ROLE` (Admin/Manager/Waiter)
- **Catalog:** `CATEGORY` (optional sort_order), `PRODUCT` (base_price, is_available, optional sort_order), `MODIFIER` (extra_price, default 0.0)
- **Operations:** `RESTAURANT_TABLE` (status: Libre/Ocupada/Reservada), `ORDER` (subtotal/taxes/tip/total_amount, status: Abierta/Pagada/Cancelada, payment_method nullable, updated_at), `ORDER_TABLE` (join table), `ORDER_ITEM` (copies unit_price at time of order), `ORDER_ITEM_MODIFIER` (copies applied_extra_price at time of order)
- **Audit:** `AUDIT_LOG` (user_id, action, optional JSON details, timestamp)

Key design decisions:
- PINs and passwords are hashed, never stored in plaintext
- `password_hash` is nullable — PIN-only users (e.g. waiters) do not need a password
- `unit_price` on `ORDER_ITEM` snapshots the price at order time (not a FK to current price)
- `applied_extra_price` on `ORDER_ITEM_MODIFIER` snapshots the modifier price at order time
- `RESTAURANT_TABLE` avoids SQL reserved keyword `TABLE`
- User name fields use `given_name`, `paternal_surname`, `maternal_surname` for clarity
- `details` on `AUDIT_LOG` stores complex changes as JSON

## Development Setup

Python virtual environment (use `.venv/`):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

SQLite is used locally (`sqlite.db` is gitignored). The `.env` file holds configuration (use `.env.example` as template).

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
