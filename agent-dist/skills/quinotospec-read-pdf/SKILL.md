---
name: Read PDF
description: Lee un archivo PDF y lo almacena en la base de datos.
trigger: ["pdf", "read pdf", "document scanning"]
scope: ["**/*.pdf"]
tools: ["run_command", "write_to_file"]
---

> **Requirements**: `pdfplumber`

# Read PDF

## Instructions
- utiliza pdfplumber para leer el archivo PDF