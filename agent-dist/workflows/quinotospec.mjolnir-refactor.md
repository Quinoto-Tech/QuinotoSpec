---
description: Flujo para generar una Propuesta de Refactor "Mjolnir" que reescribe módulos enteros bajo demanda.
---

## Datos requeridos para ejecutar el workflow

El workflow debe ser invocado con los siguientes datos. **Si falta alguno, detener el proceso y solicitar al usuario antes de continuar.**

- **nombre**: Nombre del módulo que se desea refactorizar.
- **problema**: Descripción del motivo por el que se desea refactorizar el módulo.
- **resultado_esperado**: Qué resultado se espera alcanzar a través de la refactorización.
- **detalles_adicionales**: Otras informaciones de valor (librerías, formatos, tecnologías, restricciones, etc.).

---

## Paso 1 — Inicialización del contexto

Genera el archivo `.quinoto-spec/{nombre}/mjolnir-refactor.yml` con el siguiente schema exacto:

```yaml
nombre: ""
problema: ""
resultado_esperado: ""
detalles_adicionales: ""
ultimo_paso_completado: 0
```

Completa los campos con los datos provistos. El campo `ultimo_paso_completado` se usará para reanudar el flujo si falla en algún punto.

> **⚠️ Verificación humana requerida**: Solicitar confirmación del usuario antes de continuar al paso 2. El usuario puede editar el `.yml` antes de aprobar.

Una vez confirmado, ejecuta `quinotospec-update-changelog`:
- **Título**: Mjolnir Init: {nombre}
- **Resumen**: Archivo de contexto generado en `.quinoto-spec/{nombre}/mjolnir-refactor.yml`.

---

## Paso 2 — Discovery del módulo + Mapa de Impacto

> Actualiza `ultimo_paso_completado: 1` en el `.yml` al iniciar este paso. Si falla, el proceso puede reanudarse desde aquí.

1. **Mapa de impacto previo al discovery**: Antes de analizar el módulo, identificar qué otros módulos, archivos o servicios del proyecto **importan o dependen** del módulo a refactorizar. Documentar este mapa en `.quinoto-spec/{nombre}/00-impact-map.md`.
2. Realiza un discovery completo del módulo actual siguiendo las mismas instrucciones del workflow `quinotospec.discovery`, pero guarda todos los archivos en `.quinoto-spec/{nombre}/` en lugar de `.quinoto-spec/discovery/`.
3. El archivo `07-product-and-agreements.md` debe generarse con contenido real y relevante para el contexto del refactor (no dejarlo vacío).

Una vez completado, ejecuta `quinotospec-update-changelog`:
- **Título**: Mjolnir Discovery: {nombre}
- **Resumen**: Discovery del módulo '{nombre}' generado en `.quinoto-spec/{nombre}/`. Mapa de impacto documentado.

---

## Paso 3 — Generación de la Propuesta Técnica

> Actualiza `ultimo_paso_completado: 2` en el `.yml` al iniciar este paso.

1. Vuelve a leer el archivo `.quinoto-spec/{nombre}/mjolnir-refactor.yml` por si el usuario realizó cambios desde el paso 1.
2. Ejecuta el workflow `quinotospec.create-proposal` usando como contexto:
    - Los archivos del discovery generados en `.quinoto-spec/{nombre}/`.
    - Los datos del `.yml` como `PROPOSAL_DESCRIPTION`.
    - El archivo `07-product-and-agreements.md` generado en el paso 2 debe ser la base para la sección **Alineación con Producto y Acuerdos** de la propuesta.

Una vez completado, ejecuta `quinotospec-update-changelog`:
- **Título**: Mjolnir Proposal: {nombre}
- **Resumen**: Propuesta técnica de refactor generada para el módulo '{nombre}'.

---

## Paso 4 — Generación de Historias de Usuario

> Actualiza `ultimo_paso_completado: 3` en el `.yml` al iniciar este paso.

Ejecuta el workflow `quinotospec.create-user-histories` sobre la propuesta generada en el paso 3, completando así el ciclo: propuesta → historias → listo para `create-tasks`.

Una vez completado, ejecuta `quinotospec-update-changelog`:
- **Título**: Mjolnir User Histories: {nombre}
- **Resumen**: Historias de usuario generadas para el refactor del módulo '{nombre}'.

---

## Instrucción de Reanudación

Si el proceso fue interrumpido, leer el campo `ultimo_paso_completado` del archivo `.quinoto-spec/{nombre}/mjolnir-refactor.yml` para saber desde qué paso continuar. No repetir pasos ya completados.
