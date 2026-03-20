-- =============================================================================
-- Migration: 001_initial_schema
-- Descripción: Creación del esquema inicial de SystemPOS
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. role (sin dependencias)
-- ---------------------------------------------------------------------------
CREATE TABLE role (
    id          UUID        PRIMARY KEY,
    name        VARCHAR(50) NOT NULL
);

-- ---------------------------------------------------------------------------
-- 2. branch (sin dependencias)
-- ---------------------------------------------------------------------------
CREATE TABLE branch (
    id          UUID            PRIMARY KEY,
    name        VARCHAR(150)    NOT NULL,
    address     TEXT,
    phone       VARCHAR(20),
    is_active   BOOLEAN         NOT NULL DEFAULT TRUE
);

-- ---------------------------------------------------------------------------
-- 3. tax_rate (sin dependencias)
-- ---------------------------------------------------------------------------
CREATE TABLE tax_rate (
    id          UUID            PRIMARY KEY,
    name        VARCHAR(150)    NOT NULL,
    rate        NUMERIC(5,4)    NOT NULL,
    is_default  BOOLEAN         NOT NULL DEFAULT FALSE,
    is_active   BOOLEAN         NOT NULL DEFAULT TRUE
);

-- ---------------------------------------------------------------------------
-- 4. category (sin dependencias)
-- ---------------------------------------------------------------------------
CREATE TABLE category (
    id          UUID            PRIMARY KEY,
    name        VARCHAR(150)    NOT NULL,
    description TEXT,
    sort_order  INTEGER
);

-- ---------------------------------------------------------------------------
-- 5. user (depende de role, branch)
-- ---------------------------------------------------------------------------
CREATE TABLE "user" (
    id                  UUID            PRIMARY KEY,
    branch_id           UUID            REFERENCES branch(id)
                                            ON DELETE SET NULL
                                            ON UPDATE CASCADE,
    role_id             UUID            NOT NULL REFERENCES role(id)
                                            ON DELETE RESTRICT
                                            ON UPDATE CASCADE,
    given_name          VARCHAR(150)    NOT NULL,
    paternal_surname    VARCHAR(150)    NOT NULL,
    maternal_surname    VARCHAR(150),
    email               VARCHAR(255),
    password_hash       CHAR(60),
    pin_hash            CHAR(60)        NOT NULL,
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ     NOT NULL
);

-- ---------------------------------------------------------------------------
-- 6. product (depende de category, tax_rate)
-- ---------------------------------------------------------------------------
CREATE TABLE product (
    id              UUID            PRIMARY KEY,
    category_id     UUID            NOT NULL REFERENCES category(id)
                                        ON DELETE RESTRICT
                                        ON UPDATE CASCADE,
    tax_rate_id     UUID            REFERENCES tax_rate(id)
                                        ON DELETE SET NULL
                                        ON UPDATE CASCADE,
    name            VARCHAR(150)    NOT NULL,
    base_price      NUMERIC(12,4)   NOT NULL,
    is_available    BOOLEAN         NOT NULL DEFAULT TRUE,
    sort_order      INTEGER
);

-- ---------------------------------------------------------------------------
-- 7. modifier (depende de product)
-- ---------------------------------------------------------------------------
CREATE TABLE modifier (
    id              UUID            PRIMARY KEY,
    product_id      UUID            NOT NULL REFERENCES product(id)
                                        ON DELETE RESTRICT
                                        ON UPDATE CASCADE,
    name            VARCHAR(150)    NOT NULL,
    extra_price     NUMERIC(12,4)   NOT NULL DEFAULT 0.0000
);

-- ---------------------------------------------------------------------------
-- 8. restaurant_table (depende de branch)
-- ---------------------------------------------------------------------------
CREATE TABLE restaurant_table (
    id          UUID            PRIMARY KEY,
    branch_id   UUID            NOT NULL REFERENCES branch(id)
                                    ON DELETE RESTRICT
                                    ON UPDATE CASCADE,
    identifier  VARCHAR(50)     NOT NULL,
    capacity    INTEGER,
    status      VARCHAR(50)     NOT NULL
);

-- ---------------------------------------------------------------------------
-- 9. order (depende de user)
-- ---------------------------------------------------------------------------
CREATE TABLE "order" (
    id              UUID            PRIMARY KEY,
    user_id         UUID            NOT NULL REFERENCES "user"(id)
                                        ON DELETE RESTRICT
                                        ON UPDATE CASCADE,
    subtotal        NUMERIC(12,4)   NOT NULL,
    taxes           NUMERIC(12,4)   NOT NULL,
    tip             NUMERIC(12,4)   NOT NULL DEFAULT 0.0000,
    discount        NUMERIC(12,4)   NOT NULL DEFAULT 0.0000,
    total_amount    NUMERIC(12,4)   NOT NULL,
    status          VARCHAR(50)     NOT NULL,
    payment_method  VARCHAR(50),
    created_at      TIMESTAMPTZ     NOT NULL,
    updated_at      TIMESTAMPTZ     NOT NULL
);

-- ---------------------------------------------------------------------------
-- 10. order_table (depende de order, restaurant_table)
-- ---------------------------------------------------------------------------
CREATE TABLE order_table (
    order_id    UUID        NOT NULL REFERENCES "order"(id)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE,
    table_id    UUID        NOT NULL REFERENCES restaurant_table(id)
                                ON DELETE RESTRICT
                                ON UPDATE CASCADE,
    joined_at   TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (order_id, table_id)
);

-- ---------------------------------------------------------------------------
-- 11. order_item (depende de order, product)
-- ---------------------------------------------------------------------------
CREATE TABLE order_item (
    id                  UUID            PRIMARY KEY,
    order_id            UUID            NOT NULL REFERENCES "order"(id)
                                            ON DELETE CASCADE
                                            ON UPDATE CASCADE,
    product_id          UUID            NOT NULL REFERENCES product(id)
                                            ON DELETE RESTRICT
                                            ON UPDATE CASCADE,
    quantity            INTEGER         NOT NULL,
    unit_price          NUMERIC(12,4)   NOT NULL,
    applied_tax_rate    NUMERIC(5,4)    NOT NULL,
    status              VARCHAR(50)     NOT NULL DEFAULT 'PENDING',
    notes               TEXT
);

-- ---------------------------------------------------------------------------
-- 12. order_item_modifier (depende de order_item, modifier)
-- ---------------------------------------------------------------------------
CREATE TABLE order_item_modifier (
    id                  UUID            PRIMARY KEY,
    order_item_id       UUID            NOT NULL REFERENCES order_item(id)
                                            ON DELETE CASCADE
                                            ON UPDATE CASCADE,
    modifier_id         UUID            NOT NULL REFERENCES modifier(id)
                                            ON DELETE RESTRICT
                                            ON UPDATE CASCADE,
    applied_extra_price NUMERIC(12,4)   NOT NULL
);

-- ---------------------------------------------------------------------------
-- 13. audit_log (depende de user)
-- ---------------------------------------------------------------------------
CREATE TABLE audit_log (
    id          UUID            PRIMARY KEY,
    user_id     UUID            NOT NULL REFERENCES "user"(id)
                                    ON DELETE RESTRICT
                                    ON UPDATE CASCADE,
    action      VARCHAR(100)    NOT NULL,
    details     JSONB,
    timestamp   TIMESTAMPTZ     NOT NULL
);

-- ---------------------------------------------------------------------------
-- 14. system_config (sin dependencias)
-- ---------------------------------------------------------------------------
CREATE TABLE system_config (
    key         VARCHAR(100)    PRIMARY KEY,
    value       TEXT            NOT NULL,
    description TEXT
);

-- =============================================================================
-- ÍNDICES
-- =============================================================================

-- Autenticación rápida
CREATE UNIQUE INDEX ON "user" (email) WHERE email IS NOT NULL;
CREATE UNIQUE INDEX ON "user" (pin_hash);

-- Filtros de operación frecuente
CREATE INDEX ON "order" (status);
CREATE INDEX ON "order" (user_id);
CREATE INDEX ON order_item (order_id);
CREATE INDEX ON restaurant_table (status);
CREATE INDEX ON restaurant_table (branch_id);
CREATE INDEX ON product (category_id);

-- Auditoría y trazabilidad
CREATE INDEX ON audit_log (user_id, timestamp);
CREATE INDEX ON audit_log USING GIN (details);

-- Restricción de unicidad: exactamente una tasa puede ser la default
CREATE UNIQUE INDEX ON tax_rate (is_default) WHERE is_default = TRUE;
