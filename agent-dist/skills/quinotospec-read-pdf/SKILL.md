---
name: Read PDF
description: Lee un archivo PDF, extrae su contenido y lo guarda en formato Markdown para ser usado como contexto del agente.
---

# Skill: Read PDF

Usa esta skill para ingestar documentación externa en formato PDF y convertirla en un archivo Markdown legible por el agente.

## Requisitos

- Librería Python: `pdfplumber`
- Si no está instalada: `pip install pdfplumber`

## Instrucciones de Ejecución

1. **Crear el script temporal** en `.quinoto-spec/scripts/temp_read_pdf.py`:

```python
import pdfplumber
import sys

pdf_path = sys.argv[1]
output_path = sys.argv[2]

with pdfplumber.open(pdf_path) as pdf:
    text = "\n\n".join(page.extract_text() or "" for page in pdf.pages)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(f"# Contenido extraído de: {pdf_path}\n\n")
    f.write(text)

print(f"Archivo guardado en: {output_path}")
```

2. **Ejecutar el script**:

```bash
python .quinoto-spec/scripts/temp_read_pdf.py {{DOCUMENT_PATH}} .quinoto-spec/docs/{{NOMBRE_DEL_ARCHIVO}}.md
```

3. **Verificar el output**: Leer el archivo generado y confirmar que el texto fue extraído correctamente. Si hay páginas con solo imágenes (OCR no soportado), documentarlo en el archivo de salida.

4. **Eliminar el script temporal** una vez completada la extracción.

## Convenciones

- El output siempre va en `.quinoto-spec/docs/`.
- El nombre del archivo debe ser descriptivo y en kebab-case (ej. `rapiboy-api-docs.md`).
- No dejar el script temporal en el repo.