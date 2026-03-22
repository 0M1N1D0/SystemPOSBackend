"""
run_reports.py
==============
Crea una base de datos SQLite en memoria, aplica las migraciones y el seed de
prueba, luego ejecuta 11 reportes operacionales y exporta cada uno como CSV en
el directorio reports/.

Reportes generados:
  R1  — Mesas ocupadas
  R2  — Mesas desocupadas (FREE)
  R3  — Mesas reservadas y horario
  R4  — Qué se ordenó en cada mesa
  R5  — Sucursales con mesas ocupadas
  R6  — Sucursales existentes
  R7  — Mesas por sucursal
  R8  — Empleados por sucursal
  R9  — Disponibilidad de mesas por sucursal (libres / ocupadas / reservadas)
  R10 — Horario de reservaciones (todas las CONFIRMED)
  R11 — Nota de venta por mesa (detalle completo con totales)

Uso:
    python3 scripts/run_reports.py

No requiere dependencias externas — solo Python 3.8+.
"""

import csv
import re
import sqlite3
from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
MIGRATIONS = [
    BASE_DIR / "migrations" / "001_initial_schema.sql",
    BASE_DIR / "migrations" / "002_add_reservations.sql",
]
SEEDS = [
    BASE_DIR / "seeds" / "001_test_data.sql",
]
REPORTS_DIR = BASE_DIR / "reports"


# ---------------------------------------------------------------------------
# Adaptación de SQL para SQLite
#
# Diferencias entre PostgreSQL y SQLite que requieren transformación:
#   1. Tipos TIMESTAMPTZ / JSONB → TEXT (SQLite ignora nombres desconocidos
#      pero TIMESTAMPTZ genera error de parsing en algunos builds)
#   2. CREATE INDEX ON table (...) → requiere nombre en SQLite
#   3. CREATE INDEX ... USING GIN (...) → GIN es exclusivo de PostgreSQL;
#      SQLite no lo soporta; se elimina la línea completa
# ---------------------------------------------------------------------------
_idx_counter = 0


def _next_idx_name() -> str:
    global _idx_counter
    _idx_counter += 1
    return f"_auto_idx_{_idx_counter}"


def adapt_for_sqlite(sql: str) -> str:
    # 1. Tipos de datos incompatibles
    sql = sql.replace("TIMESTAMPTZ", "TEXT").replace("JSONB", "TEXT")

    # 2. Eliminar índices GIN (no soportados por SQLite)
    sql = re.sub(r"CREATE\s+(?:UNIQUE\s+)?INDEX\s+ON\s+\w+\s+USING\s+GIN\s*\([^;]+\)\s*;",
                 "", sql, flags=re.IGNORECASE)

    # 3. Añadir nombre a índices anónimos: "CREATE [UNIQUE] INDEX ON ..."
    #    → "CREATE [UNIQUE] INDEX _auto_idx_N ON ..."
    def add_index_name(match: re.Match) -> str:
        return match.group(1) + _next_idx_name() + " " + match.group(2)

    sql = re.sub(
        r"(CREATE\s+(?:UNIQUE\s+)?INDEX\s+)(ON\s+)",
        add_index_name,
        sql,
        flags=re.IGNORECASE,
    )

    return sql


# ---------------------------------------------------------------------------
# Setup de la base de datos
# ---------------------------------------------------------------------------
def setup_db(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON")

    for path in MIGRATIONS:
        sql = adapt_for_sqlite(path.read_text(encoding="utf-8"))
        conn.executescript(sql)

    for path in SEEDS:
        sql = adapt_for_sqlite(path.read_text(encoding="utf-8"))
        conn.executescript(sql)

    conn.commit()


# ---------------------------------------------------------------------------
# Definición de los 5 reportes
# ---------------------------------------------------------------------------
REPORTS = [
    {
        "filename": "r1_mesas_ocupadas.csv",
        "title": "R1 — Mesas ocupadas",
        "sql": """
            SELECT
                b.name                                          AS sucursal,
                rt.identifier                                   AS mesa,
                rt.capacity                                     AS capacidad,
                o.status                                        AS estado_orden,
                o.created_at                                    AS hora_apertura,
                o.total_amount                                  AS total,
                u.given_name || ' ' || u.paternal_surname       AS mesero
            FROM restaurant_table rt
            JOIN branch b ON rt.branch_id = b.id
            LEFT JOIN order_table ot ON rt.id = ot.table_id
            LEFT JOIN "order" o ON ot.order_id = o.id AND o.status = 'OPEN'
            LEFT JOIN "user" u ON o.user_id = u.id
            WHERE rt.status = 'OCCUPIED'
            ORDER BY b.name, rt.identifier;
        """,
    },
    {
        "filename": "r2_mesas_libres.csv",
        "title": "R2 — Mesas desocupadas (FREE)",
        "sql": """
            SELECT
                b.name          AS sucursal,
                rt.identifier   AS mesa,
                rt.capacity     AS capacidad,
                rt.status       AS estado
            FROM restaurant_table rt
            JOIN branch b ON rt.branch_id = b.id
            WHERE rt.status = 'FREE'
            ORDER BY b.name, rt.identifier;
        """,
    },
    {
        "filename": "r3_mesas_reservadas.csv",
        "title": "R3 — Mesas reservadas y horario",
        "sql": """
            SELECT
                b.name                                          AS sucursal,
                rt.identifier                                   AS mesa,
                r.guest_name                                    AS nombre_comensal,
                r.guest_phone                                   AS telefono,
                r.party_size                                    AS personas,
                r.scheduled_at                                  AS hora_reservacion,
                r.duration_minutes                              AS duracion_min,
                r.status                                        AS estado_reservacion,
                r.notes                                         AS notas,
                u.given_name || ' ' || u.paternal_surname       AS creada_por
            FROM restaurant_table rt
            JOIN branch b ON rt.branch_id = b.id
            JOIN reservation_table rsvt ON rt.id = rsvt.table_id
            JOIN reservation r ON rsvt.reservation_id = r.id
            JOIN "user" u ON r.created_by_user_id = u.id
            WHERE rt.status = 'RESERVED'
            ORDER BY r.scheduled_at;
        """,
    },
    {
        "filename": "r4_ordenes_por_mesa.csv",
        "title": "R4 — Qué se ordenó en cada mesa",
        "sql": """
            SELECT
                b.name                                          AS sucursal,
                rt.identifier                                   AS mesa,
                o.status                                        AS estado_orden,
                p.name                                          AS producto,
                oi.quantity                                     AS cantidad,
                oi.unit_price                                   AS precio_unitario,
                ROUND(oi.quantity * oi.unit_price, 4)           AS subtotal_item,
                GROUP_CONCAT(m.name, ' | ')                     AS modificadores,
                oi.status                                       AS estado_item,
                oi.notes                                        AS notas_especiales
            FROM restaurant_table rt
            JOIN branch b ON rt.branch_id = b.id
            JOIN order_table ot ON rt.id = ot.table_id
            JOIN "order" o ON ot.order_id = o.id
            JOIN order_item oi ON o.id = oi.order_id
            JOIN product p ON oi.product_id = p.id
            LEFT JOIN order_item_modifier oim ON oi.id = oim.order_item_id
            LEFT JOIN modifier m ON oim.modifier_id = m.id
            GROUP BY
                rt.id, rt.identifier, b.name,
                o.id, o.status,
                p.name, oi.id, oi.quantity, oi.unit_price, oi.status, oi.notes
            ORDER BY b.name, rt.identifier, o.created_at, p.name;
        """,
    },
    {
        "filename": "r5_sucursales_con_mesas_ocupadas.csv",
        "title": "R5 — Sucursales con mesas ocupadas",
        "sql": """
            SELECT
                b.name                          AS sucursal,
                b.address                       AS direccion,
                b.phone                         AS telefono,
                COUNT(DISTINCT rt.id)           AS mesas_ocupadas,
                COUNT(DISTINCT o.id)            AS ordenes_activas,
                ROUND(SUM(o.total_amount), 4)   AS total_en_curso
            FROM restaurant_table rt
            JOIN branch b ON rt.branch_id = b.id
            LEFT JOIN order_table ot ON rt.id = ot.table_id
            LEFT JOIN "order" o ON ot.order_id = o.id AND o.status = 'OPEN'
            WHERE rt.status = 'OCCUPIED'
            GROUP BY b.id, b.name, b.address, b.phone
            ORDER BY b.name;
        """,
    },
    # -----------------------------------------------------------------------
    # Nuevos reportes R6–R11
    # -----------------------------------------------------------------------
    {
        "filename": "r6_sucursales.csv",
        "title": "R6 — Sucursales existentes",
        "sql": """
            SELECT
                b.name      AS sucursal,
                b.address   AS direccion,
                b.phone     AS telefono,
                CASE WHEN b.is_active THEN 'Activa' ELSE 'Inactiva' END AS estado
            FROM branch b
            ORDER BY b.name;
        """,
    },
    {
        "filename": "r7_mesas_por_sucursal.csv",
        "title": "R7 — Mesas por sucursal",
        "sql": """
            SELECT
                b.name          AS sucursal,
                rt.identifier   AS mesa,
                rt.capacity     AS capacidad,
                rt.status       AS estado
            FROM restaurant_table rt
            JOIN branch b ON rt.branch_id = b.id
            ORDER BY b.name, rt.identifier;
        """,
    },
    {
        "filename": "r8_empleados_por_sucursal.csv",
        "title": "R8 — Empleados por sucursal",
        "sql": """
            SELECT
                COALESCE(b.name, 'Sin sucursal (Admin global)')             AS sucursal,
                u.given_name
                    || ' ' || u.paternal_surname
                    || COALESCE(' ' || u.maternal_surname, '')              AS nombre_completo,
                r.name                                                      AS rol,
                COALESCE(u.email, '—')                                      AS email,
                CASE WHEN u.is_active THEN 'Activo' ELSE 'Inactivo' END    AS estado
            FROM "user" u
            JOIN role r ON u.role_id = r.id
            LEFT JOIN branch b ON u.branch_id = b.id
            ORDER BY COALESCE(b.name, 'ZZZZ'), r.name, u.paternal_surname;
        """,
    },
    {
        "filename": "r9_disponibilidad_por_sucursal.csv",
        "title": "R9 — Disponibilidad de mesas por sucursal",
        "sql": """
            SELECT
                b.name                                                          AS sucursal,
                SUM(CASE WHEN rt.status = 'FREE'     THEN 1 ELSE 0 END)        AS libres,
                SUM(CASE WHEN rt.status = 'OCCUPIED' THEN 1 ELSE 0 END)        AS ocupadas,
                SUM(CASE WHEN rt.status = 'RESERVED' THEN 1 ELSE 0 END)        AS reservadas,
                COUNT(rt.id)                                                    AS total_mesas
            FROM restaurant_table rt
            JOIN branch b ON rt.branch_id = b.id
            GROUP BY b.id, b.name
            ORDER BY b.name;
        """,
    },
    {
        "filename": "r10_horario_reservaciones.csv",
        "title": "R10 — Horario de reservaciones (CONFIRMED)",
        "sql": """
            SELECT
                b.name                                              AS sucursal,
                rt.identifier                                       AS mesa,
                r.guest_name                                        AS nombre_comensal,
                r.guest_phone                                       AS telefono,
                r.party_size                                        AS personas,
                r.scheduled_at                                      AS hora_inicio,
                r.duration_minutes                                  AS duracion_min,
                r.status                                            AS estado_reservacion,
                r.notes                                             AS notas,
                u.given_name || ' ' || u.paternal_surname           AS registrada_por
            FROM reservation r
            JOIN reservation_table rsvt ON r.id = rsvt.reservation_id
            JOIN restaurant_table rt ON rsvt.table_id = rt.id
            JOIN branch b ON rt.branch_id = b.id
            JOIN "user" u ON r.created_by_user_id = u.id
            WHERE r.status = 'CONFIRMED'
            ORDER BY r.scheduled_at;
        """,
    },
    {
        "filename": "r11_nota_de_venta.csv",
        "title": "R11 — Nota de venta por mesa",
        "sql": """
            SELECT
                b.name                                                          AS sucursal,
                rt.identifier                                                   AS mesa,
                o.id                                                            AS orden_id,
                o.created_at                                                    AS hora_apertura,
                o.updated_at                                                    AS hora_ultima_mod,
                u.given_name || ' ' || u.paternal_surname                       AS mesero,
                o.status                                                        AS estado_orden,
                COALESCE(o.payment_method, '—')                                 AS metodo_pago,
                p.name                                                          AS producto,
                oi.quantity                                                     AS cantidad,
                oi.unit_price                                                   AS precio_unitario,
                ROUND(oi.quantity * oi.unit_price, 2)                           AS importe_producto,
                COALESCE(
                    GROUP_CONCAT(m.name || ' (+$' || oim.applied_extra_price || ')', ' | '),
                    '—'
                )                                                               AS modificadores,
                ROUND(SUM(COALESCE(oim.applied_extra_price, 0)), 2)             AS extras_total,
                ROUND(
                    oi.quantity * oi.unit_price
                    + SUM(COALESCE(oim.applied_extra_price, 0)),
                    2
                )                                                               AS importe_linea,
                ROUND(oi.quantity * oi.unit_price * oi.applied_tax_rate, 2)     AS iva_linea,
                COALESCE(oi.notes, '—')                                         AS notas_especiales,
                o.subtotal                                                      AS orden_subtotal,
                o.taxes                                                         AS orden_iva,
                o.tip                                                           AS orden_propina,
                o.discount                                                      AS orden_descuento,
                o.total_amount                                                  AS orden_total
            FROM restaurant_table rt
            JOIN branch b ON rt.branch_id = b.id
            JOIN order_table ot ON rt.id = ot.table_id
            JOIN "order" o ON ot.order_id = o.id
            JOIN "user" u ON o.user_id = u.id
            JOIN order_item oi ON o.id = oi.order_id
            JOIN product p ON oi.product_id = p.id
            LEFT JOIN order_item_modifier oim ON oi.id = oim.order_item_id
            LEFT JOIN modifier m ON oim.modifier_id = m.id
            GROUP BY
                rt.id, rt.identifier, b.name,
                o.id, o.status, o.payment_method, o.created_at, o.updated_at,
                o.subtotal, o.taxes, o.tip, o.discount, o.total_amount,
                u.given_name, u.paternal_surname,
                p.name, oi.id, oi.quantity, oi.unit_price, oi.applied_tax_rate, oi.notes
            ORDER BY b.name, rt.identifier, o.created_at, p.name;
        """,
    },
]


# ---------------------------------------------------------------------------
# Exportar un reporte a CSV
# ---------------------------------------------------------------------------
def export_report(conn: sqlite3.Connection, report: dict) -> int:
    cursor = conn.execute(report["sql"])
    headers = [description[0] for description in cursor.description]
    rows = cursor.fetchall()

    output_path = REPORTS_DIR / report["filename"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    return len(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(":memory:")
    try:
        print("Inicializando base de datos...")
        setup_db(conn)
        print("  ✓ Migraciones aplicadas")
        print("  ✓ Seed cargado\n")

        print("Ejecutando reportes:")
        print("-" * 60)
        for report in REPORTS:
            row_count = export_report(conn, report)
            print(f"  {report['title']}")
            print(f"    → {report['filename']}  ({row_count} fila(s))")

        print("-" * 60)
        print(f"\nCSVs generados en: {REPORTS_DIR}")
        print("Importa cada archivo en Google Sheets via Archivo > Importar.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
