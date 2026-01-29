---
name: Quinotospec Stack Detect
description: Identifies the project's technology stack (language, frameworks, test runners, etc.) by analyzing key configuration files.
---

# Quinotospec Stack Detect

Esta skill permite al agente identificar automáticamente las tecnologías utilizadas en el proyecto. 

## Instrucciones de Análisis

Para detectar el stack técnico, busca y analiza los siguientes archivos en la raíz del proyecto:

### 1. Lenguajes y Frameworks Principales
- **JavaScript/TypeScript**: `package.json` (Busca en `dependencies` y `devDependencies`).
- **Python**: `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`.
- **Go**: `go.mod`.
- **Rust**: `Cargo.toml`.
- **PHP**: `composer.json`.
- **Java/Kotlin**: `pom.xml`, `build.gradle`.
- **Ruby**: `Gemfile`.

### 2. Testing Frameworks
- **Python**: `pytest`, `unittest`, `tox`.
- **JavaScript**: `jest`, `vitest`, `mocha`, `cypress`, `playwright`.
- **Go**: `testing` (estándar).

### 3. Herramientas de DevOps y CI/CD
- **Docker**: `Dockerfile`, `docker-compose.yml`.
- **GitHub Actions**: `.github/workflows/`.
- **Husky/Lint-staged**: Configuraciones en `package.json`.

## Formato de Salida Esperado

Genera un resumen en formato Markdown (será guardado en `.quinoto-spec/discovery/00-stack-profile.md`) con la siguiente estructura:

```markdown
# 🛠️ Stack Profile: [Nombre del Proyecto]

## 🏗️ Core Technologies
- **Language:** [e.g. Python 3.10+]
- **Primary Framework:** [e.g. Django 4.2]
- **Package Manager:** [e.g. pipenv]

## 🧪 Quality & Testing
- **Test Runner:** [e.g. Pytest]
- **Linter/Formatter:** [e.g. Black, Flake8]

## 🚢 Infrastructure & DevOps
- **Containerization:** [e.g. Docker]
- **CI/CD:** [e.g. GitHub Actions]

## 📝 Coding Standards (Detected)
- [Ej: "Usa Service Layer", "Arquitectura Hexagonal", "Strict Typing"]
```

## Ejemplo de Detección

Si se encuentra un `package.json` con `"next": "14.x"` y `"vitest": "1.x"`, el perfil debe reflejar:
- Core: Next.js (React)
- Testing: Vitest
