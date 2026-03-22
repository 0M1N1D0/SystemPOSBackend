-- =============================================================================
-- Migration: 002_add_reservations
-- Descripción: Agrega gestión de reservaciones con soporte para mesas unidas
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 15. reservation (depende de branch, user, order)
-- ---------------------------------------------------------------------------
CREATE TABLE reservation (
    id                  UUID            PRIMARY KEY,
    branch_id           UUID            NOT NULL REFERENCES branch(id)
                                            ON DELETE RESTRICT
                                            ON UPDATE CASCADE,
    created_by_user_id  UUID            NOT NULL REFERENCES "user"(id)
                                            ON DELETE RESTRICT
                                            ON UPDATE CASCADE,
    order_id            UUID            REFERENCES "order"(id)
                                            ON DELETE SET NULL
                                            ON UPDATE CASCADE,
    guest_name          VARCHAR(150)    NOT NULL,
    guest_phone         VARCHAR(20),
    party_size          INTEGER         NOT NULL,
    scheduled_at        TIMESTAMPTZ     NOT NULL,
    duration_minutes    INTEGER         NOT NULL DEFAULT 90,
    status              VARCHAR(50)     NOT NULL DEFAULT 'CONFIRMED',
    notes               TEXT,
    created_at          TIMESTAMPTZ     NOT NULL,
    updated_at          TIMESTAMPTZ     NOT NULL
);

-- ---------------------------------------------------------------------------
-- 16. reservation_table (depende de reservation, restaurant_table)
--     Patrón idéntico a order_table: PK compuesta sin UUID propio.
--     Permite reservar múltiples mesas unidas para grupos grandes.
-- ---------------------------------------------------------------------------
CREATE TABLE reservation_table (
    reservation_id  UUID        NOT NULL REFERENCES reservation(id)
                                    ON DELETE CASCADE
                                    ON UPDATE CASCADE,
    table_id        UUID        NOT NULL REFERENCES restaurant_table(id)
                                    ON DELETE RESTRICT
                                    ON UPDATE CASCADE,
    PRIMARY KEY (reservation_id, table_id)
);

-- =============================================================================
-- ÍNDICES
-- =============================================================================

-- Consulta principal de operaciones: reservaciones activas de una sucursal por fecha
-- Es un índice parcial — excluye SEATED/CANCELLED/NO_SHOW para mayor eficiencia
CREATE INDEX ON reservation (branch_id, scheduled_at) WHERE status = 'CONFIRMED';

-- Índice completo para reportes históricos (todas las reservaciones por sucursal)
CREATE INDEX ON reservation (branch_id, scheduled_at);

-- Filtro por estado
CREATE INDEX ON reservation (status);

-- Trazabilidad del staff
CREATE INDEX ON reservation (created_by_user_id);

-- Enlace con orden (búsqueda inversa poco frecuente)
CREATE INDEX ON reservation (order_id) WHERE order_id IS NOT NULL;

-- reservation_table: búsqueda inversa "¿qué reservaciones tiene esta mesa?"
-- Clave para la validación de solapamiento de franjas horarias
CREATE INDEX ON reservation_table (table_id);
