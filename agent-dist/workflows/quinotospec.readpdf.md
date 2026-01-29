---
description: Ingesta de documentación PDF para contexto del agente
---

**Documento:** {{DOCUMENT_PATH}}
**Nombre de salida:** {{NOMBRE_DEL_ARCHIVO}}

### Instrucciones:
1. Utiliza la skill `quinotospec-read-pdf` (o herramienta equivalente) para extraer el texto del archivo PDF.
2. Crea el archivo `.quinoto-spec/discovery/{{NOMBRE_DEL_ARCHIVO}}.md`.
3. Formatea el contenido en Markdown para asegurar que sea fácilmente procesable.

**Instrucción Final OBLIGATORIA (Changelog):**
DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: PDF Ingested: {{NOMBRE_DEL_ARCHIVO}}
- **Resumen**: Se procesó el documento '{{DOCUMENT_PATH}}' y se añadió el contexto extraído a la documentación.