# Ejemplo: Node.js Express con QuinotoSpec

Proyecto de ejemplo mostrando QuinotoSpec con Node.js + Express + Jest.

## Stack

- **Lenguaje**: JavaScript (Node.js 18+)
- **Framework**: Express
- **Package Manager**: npm
- **Testing**: Jest + Supertest

## Estructura

```
node-express/
├── .quinoto-spec/           # Configuración QuinotoSpec
│   ├── discovery/           # 8 archivos de discovery
│   ├── proposals/           # Propuestas técnicas
│   └── prefix-registry.md   # Prefijos registrados
├── src/
│   ├── index.js             # Aplicación Express
│   └── routes/
│       └── users.js         # Endpoints de usuarios
├── tests/
│   └── users.test.js        # Tests de usuarios
├── package.json
└── README.md
```

## Setup

```bash
# Instalar dependencias
npm install

# Ejecutar aplicación
npm start

# Ejecutar tests
npm test

# Ejecutar con cobertura
npm run test:coverage
```

## Uso con QuinotoSpec

### 1. Discovery
```bash
@quinotospec.discovery
```

### 2. Crear Propuesta
```bash
@quinotospec.create-proposal
# Descripción: "Agregar autenticación JWT con refresh tokens"
```

### 3. Generar Historias de Usuario
```bash
@quinotospec.create-user-stories --slug auth-jwt
```

### 4. Generar Tareas
```bash
@quinotospec.create-tasks --slug auth-jwt
```

### 5. Implementar
```bash
@quinotospec.apply --task-id TSK-AUTH-001
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/users` | Listar usuarios |
| POST | `/users` | Crear usuario |
| GET | `/users/:id` | Obtener usuario |
