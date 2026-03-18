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
- Entities mirror the DB schema: `User`, `Role`, `Category`, `Product`, `Modifier`, `RestaurantTable`, `Order`, `OrderTable`, `OrderItem`, `OrderItemModifier`, `AuditLog`
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
- `decimal.Decimal` for monetary values (not `float`) — base_price, unit_price, applied_extra_price, subtotal, taxes, tip, total_amount
- Raise domain exceptions for business rule violations; let the presentation layer catch and map to HTTP errors
- No mutable default arguments

---

## Project-Specific Rules

- `TABLE` is a SQL reserved word — the entity is `RestaurantTable` / `RESTAURANT_TABLE`
- `password_hash` is nullable — PIN-only users (waiters) don't need a password
- `unit_price` on `OrderItem` and `applied_extra_price` on `OrderItemModifier` are price snapshots, never FKs to the catalog
- User name fields: `given_name`, `paternal_surname`, `maternal_surname`
- Auth has two paths: PIN (POS terminal) and email+password (web dashboard)
- All IDs are UUIDs

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
