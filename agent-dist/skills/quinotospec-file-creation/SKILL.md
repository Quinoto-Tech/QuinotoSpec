---
name: quinotospec-file-creation
description: Estandares y convenciones para crear archivos, en especial scripts temporales.
---

# Creacion de Archivos y Scripts

## Scripts temporales
Cuando crees scripts para tareas puntuales, migraciones de datos, interacciones temporales (por ejemplo con PDFs o APIs) o snippets de prueba:

1. **Ubicacion**: SIEMPRE en el directorio `.quinoto-spec/scripts/` en la raiz del proyecto.
2. **Convencion de nombre**: prefija el archivo con `temp_`.
    - Ejemplo: `.quinoto-spec/scripts/temp_read_pdf.py`

## Uso
- No crees archivos de script en la raiz del proyecto.
- Verifica que el directorio `.quinoto-spec/scripts/` exista antes de escribir.
- Los scripts temporales no se commitean: limpialos al terminar la tarea (o usa `scripts/cleanup-temp.sh`).
