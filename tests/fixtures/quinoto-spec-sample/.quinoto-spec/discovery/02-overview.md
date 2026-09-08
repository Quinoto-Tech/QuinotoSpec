# Discovery: Overview

## Resumen Ejecutivo
Proyecto de ejemplo (fixture) que simula un backend de autenticación y pagos. Se usa
únicamente para probar de forma reproducible las skills nórdicas de QuinotoSpec
(Mimir, Valkyrie, Bifrost) contra un `.quinoto-spec/` con contenido realista.

## Estructura de Carpetas
- `src/auth/` — login, sesiones, JWT, 2FA
- `src/payments/` — checkout, refunds
- `src/reports/` — reportes legacy (baja prioridad)

## Pre-requisitos
- Node.js 20+
- PostgreSQL 15+
