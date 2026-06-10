# Ejemplo: Rust Axum con QuinotoSpec

Proyecto de ejemplo mostrando QuinotoSpec con Rust + Axum.

## Stack

- **Lenguaje**: Rust
- **Framework**: Axum
- **Package Manager**: Cargo
- **Testing**: cargo test

## Estructura

```
rust-axum/
├── .quinoto-spec/           # Configuración QuinotoSpec
│   ├── discovery/           # 8 archivos de discovery
│   ├── proposals/           # Propuestas técnicas
│   └── prefix-registry.md   # Prefijos registrados
├── src/
│   ├── main.rs              # Aplicación Axum
│   ├── routes/
│   │   └── users.rs         # Endpoints de usuarios
│   └── models/
│       └── user.rs          # Modelos de datos
├── tests/
│   └── api_tests.rs         # Tests de API
├── Cargo.toml
└── README.md
```

## Setup

```bash
# Compilar proyecto
cargo build

# Ejecutar aplicación
cargo run

# Ejecutar tests
cargo test

# Ejecutar con cobertura (requiere cargo-tarpaulin)
cargo tarpaulin --out Html
```

## Uso con QuinotoSpec

### 1. Discovery
```bash
@quinotospec.discovery
```

### 2. Crear Propuesta
```bash
@quinotospec.create-proposal
# Descripción: "Implementar sistema de caché Redis para respuestas"
```

### 3. Generar Historias de Usuario
```bash
@quinotospec.create-user-stories --slug redis-cache
```

### 4. Generar Tareas
```bash
@quinotospec.create-tasks --slug redis-cache
```

### 5. Implementar
```bash
@quinotospec.apply --task-id TSK-CACHE-001
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/users` | Listar usuarios |
| POST | `/users` | Crear usuario |
| GET | `/users/:id` | Obtener usuario |
| DELETE | `/users/:id` | Eliminar usuario |
