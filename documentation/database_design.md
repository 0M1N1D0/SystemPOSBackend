# Diseño de Base de Datos: System POS

Este documento presenta el modelo relacional propuesto para el backend del sistema, enfocado en escalabilidad y trazabilidad.

## Diagrama de Entidad-Relación (ERD)

```mermaid
erDiagram
    USER ||--o{ ORDER : "toma"
    USER ||--o{ AUDIT_LOG : "genera"
    ROLE ||--o{ USER : "define"
    
    CATEGORY ||--o{ PRODUCT : "contiene"
    PRODUCT ||--o{ MODIFIER : "tiene"
    PRODUCT ||--o{ ORDER_ITEM : "se incluye en"
    
    TABLE ||--o{ ORDER : "pertenece a"
    
    ORDER ||--o{ ORDER_ITEM : "contiene"
    ORDER_ITEM ||--o{ ORDER_ITEM_MODIFIER : "tiene"
    MODIFIER ||--o{ ORDER_ITEM_MODIFIER : "aplicado en"

    USER {
        uuid id PK
        string name "Mandatorio"
        string first_name "Mandatorio (Apellido Paterno)"
        string second_name "Opcional (Apellido Materno)"
        string email "Mandatorio, Único (Recuperación/Admin)"
        string password_hash "Mandatorio (Solo para Dashboard)"
        string pin_hash "Mandatorio, Único (Login POS - 6 dígitos)"
        uuid role_id FK "Mandatorio"
        datetime created_at "Mandatorio"
    }

    ROLE {
        uuid id PK
        string name "Mandatorio (Admin, Gerente, Mesero)"
    }

    CATEGORY {
        uuid id PK
        string name "Mandatorio"
        string description "Opcional"
    }

    PRODUCT {
        uuid id PK
        uuid category_id FK "Mandatorio"
        string name "Mandatorio"
        float base_price "Mandatorio"
        boolean is_available "Mandatorio, Default: True"
    }

    MODIFIER {
        uuid id PK
        uuid product_id FK "Mandatorio"
        string name "Mandatorio"
        float extra_price "Mandatorio, Default: 0.0"
    }

    TABLE {
        uuid id PK
        string identifier "Mandatorio (Ej. Mesa 1)"
        integer capacity "Opcional"
        string status "Mandatorio (Libre, Ocupada, Reservada)"
    }

    ORDER {
        uuid id PK
        uuid table_id FK "Mandatorio"
        uuid user_id FK "Mandatorio (Mesero)"
        float subtotal "Mandatorio"
        float taxes "Mandatorio"
        float tip "Opcional (Default: 0.0)"
        float total_amount "Mandatorio"
        string status "Mandatorio (Abierta, Pagada, Cancelada)"
        datetime created_at "Mandatorio"
    }

    ORDER_ITEM {
        uuid id PK
        uuid order_id FK "Mandatorio"
        uuid product_id FK "Mandatorio"
        integer quantity "Mandatorio"
        float unit_price "Mandatorio (Copia del precio actual)"
        string notes "Opcional"
    }

    ORDER_ITEM_MODIFIER {
        uuid id PK
        uuid order_item_id FK "Mandatorio"
        uuid modifier_id FK "Mandatorio"
    }

    AUDIT_LOG {
        uuid id PK
        uuid user_id FK "Mandatorio"
        string action "Mandatorio"
        string details "Opcional (JSON)"
        datetime timestamp "Mandatorio"
    }
```

## Descripción de Módulos (Detalle de Obligatoriedad)

### 1. Gestión de Datos Maestros
- **Categorías y Productos**: El nombre y precio son siempre obligatorios. La descripción de la categoría es opcional para dar flexibilidad.
- **Modificadores**: El precio extra es obligatorio pero puede ser `0.0` por defecto.

### 2. Seguridad y Autenticación
- **PIN (6 dígitos)**: Se utiliza como identificador principal para el login rápido en la terminal POS (Tablets). Se define un PIN de 6 dígitos para permitir hasta 1,000,000 de combinaciones únicas, garantizando escalabilidad y mayor seguridad que un PIN de 4 dígitos.
- **pin_hash**: Siguiendo la Arquitectura Limpia, el PIN nunca se guarda en texto plano; se almacena su hash para protección de datos.
- **Dual Authentication**: El `email` y `password_hash` se reservan para el acceso administrativo al Dashboard Web, donde se requiere una seguridad más robusta.

### 3. Operaciones
- **Notas en ítems**: Totalmente opcional, usado para instrucciones especiales a cocina (ej: "sin cebolla").
- **Propinas**: Opcional, permitiendo registrar órdenes sin propina pre-cargada.
- **Logs de Auditoría**: El campo `details` es opcional para acciones simples, pero almacenará cambios complejos en formato JSON cuando sea necesario.
