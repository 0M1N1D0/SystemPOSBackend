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

    RESTAURANT_TABLE ||--o{ ORDER_TABLE : "asociada a"
    ORDER ||--o{ ORDER_TABLE : "posee"

    ORDER ||--o{ ORDER_ITEM : "contiene"
    ORDER_ITEM ||--o{ ORDER_ITEM_MODIFIER : "tiene"
    MODIFIER ||--o{ ORDER_ITEM_MODIFIER : "aplicado en"

    USER {
        uuid id PK
        string given_name "Mandatorio"
        string paternal_surname "Mandatorio"
        string maternal_surname "Opcional"
        string email "Mandatorio, Único (Recuperación/Admin)"
        string password_hash "Opcional (Solo para Dashboard)"
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
        integer sort_order "Opcional (Orden de visualización en menú)"
    }

    PRODUCT {
        uuid id PK
        uuid category_id FK "Mandatorio"
        string name "Mandatorio"
        float base_price "Mandatorio"
        boolean is_available "Mandatorio, Default: True"
        integer sort_order "Opcional (Orden de visualización en menú)"
    }

    MODIFIER {
        uuid id PK
        uuid product_id FK "Mandatorio"
        string name "Mandatorio"
        float extra_price "Mandatorio, Default: 0.0"
    }

    RESTAURANT_TABLE {
        uuid id PK
        string identifier "Mandatorio (Ej. Mesa 1)"
        integer capacity "Opcional"
        string status "Mandatorio (Libre, Ocupada, Reservada)"
    }

    ORDER {
        uuid id PK
        uuid user_id FK "Mandatorio (Mesero)"
        float subtotal "Mandatorio"
        float taxes "Mandatorio"
        float tip "Opcional (Default: 0.0)"
        float total_amount "Mandatorio"
        string status "Mandatorio (Abierta, Pagada, Cancelada)"
        string payment_method "Opcional (Efectivo, Tarjeta, Transferencia)"
        datetime created_at "Mandatorio"
        datetime updated_at "Mandatorio"
    }

    ORDER_TABLE {
        uuid order_id FK "Mandatorio"
        uuid table_id FK "Mandatorio"
        datetime joined_at "Mandatorio"
    }

    ORDER_ITEM {
        uuid id PK
        uuid order_id FK "Mandatorio"
        uuid product_id FK "Mandatorio"
        integer quantity "Mandatorio"
        float unit_price "Mandatorio (Copia del precio al momento de la orden)"
        string notes "Opcional"
    }

    ORDER_ITEM_MODIFIER {
        uuid id PK
        uuid order_item_id FK "Mandatorio"
        uuid modifier_id FK "Mandatorio"
        float applied_extra_price "Mandatorio (Copia del precio extra al momento de la orden)"
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
- **sort_order**: Campo opcional en `CATEGORY` y `PRODUCT` para controlar el orden de visualización en el menú de la tablet. Sin él, el orden quedaría atado al `id` o al momento de inserción.

### 2. Seguridad y Autenticación
- **PIN (6 dígitos)**: Se utiliza como identificador principal para el login rápido en la terminal POS (Tablets). Se define un PIN de 6 dígitos para permitir hasta 1,000,000 de combinaciones únicas, garantizando escalabilidad y mayor seguridad que un PIN de 4 dígitos.
- **pin_hash**: Siguiendo la Arquitectura Limpia, el PIN nunca se guarda en texto plano; se almacena su hash para protección de datos.
- **Dual Authentication**: El `email` y `password_hash` se reservan para el acceso administrativo al Dashboard Web, donde se requiere una seguridad más robusta. `password_hash` es **nullable** — un usuario que solo opera la terminal POS no necesita contraseña.

### 3. Operaciones
- **Notas en ítems**: Totalmente opcional, usado para instrucciones especiales a cocina (ej: "sin cebolla").
- **Propinas**: Opcional, permitiendo registrar órdenes sin propina pre-cargada.
- **payment_method**: Nullable mientras la orden está abierta. Se registra al momento del pago para permitir cierre de caja por método de pago (efectivo, tarjeta, transferencia).
- **updated_at en ORDER**: Registra la última modificación de la orden, necesario para auditoría y reportes de tiempo de atención.
- **Snapshot de precios**: Tanto `unit_price` en `ORDER_ITEM` como `applied_extra_price` en `ORDER_ITEM_MODIFIER` copian el precio vigente al momento de crear la orden. Esto garantiza que los tickets históricos sean inmutables ante cambios futuros en el catálogo.
- **Logs de Auditoría**: El campo `details` es opcional para acciones simples, pero almacenará cambios complejos en formato JSON cuando sea necesario.

## Notas de Diseño

### Nombres de campos USER
Los campos de nombre usan terminología en inglés coherente con el dominio:
- `given_name` → nombre de pila
- `paternal_surname` → apellido paterno
- `maternal_surname` → apellido materno (opcional)

Esto evita la confusión de usar `first_name` para referirse a un apellido.

### RESTAURANT_TABLE (antes TABLE)
La entidad se nombra `RESTAURANT_TABLE` en lugar de `TABLE` porque `TABLE` es una palabra reservada en SQL estándar y SQLite, lo que causaría errores o requeriría escapado constante en todas las consultas.

### MODIFIER acoplado a producto
Cada modificador tiene `product_id FK`, lo que significa que modificadores con el mismo nombre para distintos productos son registros separados. Para el alcance actual (MVP) esto es aceptable; una refactorización futura podría introducir un `MODIFIER_GROUP` compartido.

### ROLE sin permisos granulares
Los roles son etiquetas (Admin/Gerente/Mesero). Si en el futuro se necesitan permisos por funcionalidad, se requeriría agregar una tabla de permisos. Para el alcance actual es suficiente.
