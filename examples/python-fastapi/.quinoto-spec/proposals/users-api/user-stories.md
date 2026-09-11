# User Stories — API de usuarios CRUD (USRS-9k1m)

## US-001 — Listar usuarios

**Como** consumidor de la API
**quiero** listar los usuarios registrados
**para** ver el estado actual del sistema

**Criterios de aceptacion**
- [x] `GET /users/` responde 200 con lista JSON
- [x] Lista vacia inicialmente

## US-002 — Crear usuario

**Como** consumidor de la API
**quiero** crear un usuario con username y email
**para** registrar cuentas nuevas

**Criterios de aceptacion**
- [x] `POST /users/` responde 201 con el usuario creado (incluye `id`)
- [x] Validacion de campos via pydantic

## US-003 — Obtener usuario por id

**Como** consumidor de la API
**quiero** consultar un usuario por su id
**para** ver sus datos

**Criterios de aceptacion**
- [x] `GET /users/{id}` responde 200 si existe
- [x] Responde 404 si no existe
