Generate or review code for the SystemPOS Backend following these mandatory constraints:

## Clean Architecture — Layer Rules

```
Domain Layer (innermost)
  └─ Application Layer
       └─ Infrastructure Layer
            └─ Presentation Layer (outermost)
```

**Strict dependency rule: inner layers NEVER import from outer layers.**

### Domain Layer (`app/domain/`)
- Pure Python dataclasses or simple classes — zero framework imports
- Entities mirror the DB schema: `Branch`, `User`, `Role`, `TaxRate`, `Category`, `Product`, `Modifier`, `RestaurantTable`, `Order`, `OrderTable`, `OrderItem`, `OrderItemModifier`, `Reservation`, `ReservationTable`, `AuditLog`, `SystemConfig`
- Repository interfaces (abstract base classes) defined here, implemented in Infrastructure
- Domain exceptions defined here (e.g. `OrderAlreadyClosedError`)
- No SQLAlchemy, no FastAPI, no Pydantic here

### Application Layer (`app/application/`)
- Use cases (one class per use case, e.g. `CreateOrderUseCase`, `AuthenticateWithPinUseCase`)
- Each use case receives its dependencies (repos, services) via constructor injection
- Returns domain entities or simple DTOs — never ORM models or HTTP responses
- Business logic lives here, not in controllers or repositories

### Infrastructure Layer (`app/infrastructure/`)
- SQLAlchemy ORM models (separate from domain entities)
- Repository implementations that satisfy domain interfaces
- Mappers between ORM models and domain entities
- External service adapters (email, etc.)

### Presentation Layer (`app/presentation/`)
- FastAPI routers/controllers only
- Pydantic request/response schemas
- Calls use cases — never touches repositories or domain entities directly
- Maps use case output to HTTP responses

---

## SOLID Principles — Checklist

- **S** — Each class has one reason to change. Use cases do ONE thing.
- **O** — Extend via new classes, not by modifying existing ones (new use case = new file).
- **L** — Repository implementations are interchangeable with their interfaces.
- **I** — Small, focused interfaces. Don't force classes to implement methods they don't use.
- **D** — Depend on abstractions (interfaces), not concretions. Inject dependencies via constructor.

---

## Python Best Practices

- Type hints on all function signatures
- Abstract base classes (`ABC`, `abstractmethod`) for interfaces
- Dataclasses for domain entities where appropriate
- `uuid.UUID` type for all IDs (not raw strings)
- `decimal.Decimal` for monetary values (not `float`) — base_price, unit_price, applied_extra_price, subtotal, taxes, tip, discount, total_amount, tax rates
- DB column types: `NUMERIC(12,4)` for prices/amounts, `NUMERIC(5,4)` for rates, `CHAR(60)` for bcrypt hashes, `JSONB` for `AUDIT_LOG.details`, `VARCHAR(n)` for bounded strings, `TEXT` for unbounded strings
- Raise domain exceptions for business rule violations; let the presentation layer catch and map to HTTP errors
- No mutable default arguments

---

## Domain Enums (defined in `app/domain/enums.py`)

All enums use `str, Enum` so they serialize as readable strings in DB and JSON.

```
RoleName:           ADMIN | MANAGER | WAITER
TableStatus:        FREE | OCCUPIED | RESERVED
OrderStatus:        OPEN | PAID | CANCELLED
PaymentMethod:      CASH | CARD | TRANSFER
OrderItemStatus:    PENDING | IN_PREPARATION | READY | DELIVERED | CANCELLED
ReservationStatus:  CONFIRMED | SEATED | CANCELLED | NO_SHOW
  (SEATED, CANCELLED, NO_SHOW are terminal states — no further transitions allowed; validated in domain entity)

AuditAction:
  Auth:         USER_LOGIN, USER_LOGOUT, USER_LOGIN_FAILED
  Users:        USER_CREATED, USER_UPDATED, USER_DEACTIVATED,
                USER_PIN_CHANGED, USER_PASSWORD_CHANGED
  Catalog:      CATEGORY_CREATED, CATEGORY_UPDATED,
                PRODUCT_CREATED, PRODUCT_UPDATED, PRODUCT_PRICE_UPDATED, PRODUCT_TOGGLED,
                MODIFIER_CREATED, MODIFIER_UPDATED, MODIFIER_DELETED
  Tax:          TAX_RATE_CREATED, TAX_RATE_UPDATED,
                TAX_RATE_DEACTIVATED, TAX_RATE_DEFAULT_CHANGED
  Orders:       ORDER_CREATED, ORDER_ITEM_ADDED, ORDER_ITEM_REMOVED, ORDER_ITEM_UPDATED,
                ORDER_PAID, ORDER_CANCELLED, DISCOUNT_APPLIED,
                TABLE_ASSIGNED, TABLE_RELEASED
  Reservations: RESERVATION_CREATED, RESERVATION_UPDATED, RESERVATION_CANCELLED,
                RESERVATION_SEATED, RESERVATION_NO_SHOW
```

Never use raw strings for these values in use cases or repositories.

## Project-Specific Rules

- `TABLE` is a SQL reserved word — the entity is `RestaurantTable` / `RESTAURANT_TABLE`
- `password_hash` and `email` are nullable — PIN-only users (waiters) don't need either
- `User.is_active` enables soft delete — never hard-delete users with order or audit history
- `unit_price` on `OrderItem` and `applied_extra_price` on `OrderItemModifier` are price snapshots, never FKs to the catalog
- `Order.total_amount` = `subtotal + taxes + tip - discount`
- `Order.discount` stores the applied discount amount (result of `DISCOUNT_APPLIED` audit events)
- `OrderItem.status` defaults to `PENDING` — used for KDS (Kitchen Display System) integration
- `OrderTable` has composite PK `(order_id, table_id)` — no UUID needed on the join table
- `TAX_RATE.is_default` uniqueness enforced by partial unique index in the DB (only one TRUE allowed)
- `RestaurantTable.branch_id` is NOT NULL — every table belongs to a branch
- `User.branch_id` is nullable — Admin users may not be tied to a specific branch
- User name fields: `given_name`, `paternal_surname`, `maternal_surname`
- Auth has two paths: PIN (POS terminal) and email+password (web dashboard)
- All entity IDs are UUIDs generated in Python (`uuid.uuid4()`), not by PostgreSQL
- Never use `float` for monetary or rate values — always `decimal.Decimal` in Python, `NUMERIC` in PostgreSQL
- `Reservation.branch_id` is NOT NULL and denormalized (also reachable via `reservation_table → restaurant_table`) for efficient branch-level queries
- `Reservation.order_id` is nullable — linked when guest arrives and a new order is opened (`RESERVATION_SEATED`)
- `Reservation.duration_minutes` defaults to 90 — defines estimated end time (`scheduled_at + duration_minutes`)
- `ReservationTable` has composite PK `(reservation_id, table_id)` — no UUID needed; mirrors `OrderTable` pattern
- Overlap validation (two `CONFIRMED` reservations for the same table in the same time slot) is a domain rule enforced in the use case, not a DB constraint
- `RestaurantTable.status = RESERVED` is set by the use case when a `CONFIRMED` reservation falls within the `reservation_upcoming_threshold_minutes` threshold (stored in `SYSTEM_CONFIG`); never use DB triggers
- `ReservationStatus` terminal states (`SEATED`, `CANCELLED`, `NO_SHOW`) must be validated in the domain entity — no transitions out of terminal states

---

## Suggested File Structure

```
app/
├── domain/
│   ├── entities/          # Pure Python entities
│   ├── repositories/      # Abstract interfaces (ABC)
│   └── exceptions.py
├── application/
│   └── use_cases/         # One file per use case
├── infrastructure/
│   ├── orm/               # SQLAlchemy models
│   ├── repositories/      # Concrete implementations
│   └── mappers/           # ORM ↔ Domain mappers
└── presentation/
    ├── routers/            # FastAPI routers
    └── schemas/            # Pydantic request/response models
```

---

Before generating any code, state which layer it belongs to and confirm it has no illegal dependencies on outer layers.
