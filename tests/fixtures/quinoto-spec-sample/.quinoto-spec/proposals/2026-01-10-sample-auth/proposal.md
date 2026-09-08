# Propuesta Técnica: Sample Auth JWT

**Prefijo:** AUTH-a1b2
**Fecha de Creación**: 2026-01-10
**Estado**: 🟢 En Curso
**Prioridad**: P1
**Complejidad**: Media
**Servicios Afectados**: auth-service, gateway, notification-service
**Party Mode**: — No ejecutado

---

## Resumen Ejecutivo

Fortalecer el login del `auth-service` agregando autenticación de dos factores (2FA)
basada en TOTP, reduciendo el riesgo de compromiso de cuentas detectado en el último
audit de seguridad.

## Problema Actual

- El login solo requiere usuario y contraseña.
- Se detectaron intentos de credential stuffing en `gateway`.
- No hay mecanismo de segundo factor disponible para usuarios ni administradores.

## Alternativas Consideradas

| Alternativa | Pros | Contras | Descartada porque |
|---|---|---|---|
| SMS OTP | Simple para el usuario | Costo por SMS, vulnerable a SIM swapping | Riesgo de seguridad mayor que TOTP |
| TOTP (elegida) | Estándar abierto, sin costo por verificación, offline | Requiere app externa (ej. Authenticator) | — |

## Solución Propuesta

Implementar TOTP como mecanismo de 2FA opcional (obligatorio para roles admin),
integrado en el flujo de login existente de `auth-service`.

## Beneficios

- Reduce superficie de ataque de credential stuffing.
- Cumple con el hallazgo de seguridad #3 del último discovery.

## Alineación con Producto y Acuerdos

- Visión de Producto: alineado con el objetivo de "confianza y seguridad" del roadmap.
- KPIs Impactados: tasa de cuentas comprometidas.
- Cumplimiento de DoR: ✅ completo.

## Especificación Técnica Detallada

### auth
- **AGREGA**: soporte TOTP para 2FA → ver `delta-specs/auth/spec.md#added-requirements`

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Usuarios pierden acceso a su app TOTP | Media | Alto | Códigos de recuperación de un solo uso |

## Plan de Implementación

1. **User Stories** → `user-stories.md`
2. **Delta Specs** → `delta-specs/auth/spec.md`
3. **Apply** → implementación incremental con tests
4. **Changelog** → trazabilidad vía `quinotospec-update-changelog`

## Criterios de Aceptación (DoD)

- [ ] Usuario puede activar/desactivar 2FA desde su perfil.
- [ ] Login rechaza códigos TOTP inválidos o expirados.
- [ ] Tests automatizados cubren el flujo completo de 2FA.

## Plan de Verificación

- Tests manuales: activar 2FA, hacer login con código válido e inválido.
- Tests automatizados: unit + integration sobre `auth-service`.
- Criterio de éxito: 0 incidentes de credential stuffing exitoso en 30 días post-release.

## Impacto en el Sistema

- Archivos nuevos/modificados: `src/auth/totp.ts`, `src/auth/login.controller.ts`.
- Dependencias: librería TOTP estándar (RFC 6238).

## Conclusión

**Aprobación Requerida**: Sí
**Estimación Total**: 2 sprints
**Prioridad**: P1
**Fecha Límite Sugerida**: 2026-02-15
