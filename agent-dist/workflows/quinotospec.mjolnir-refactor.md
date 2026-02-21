---
description: Flujo para generar una Propuesta de Refactor "Mjolnir" que reescribe módulos enteros bajo demanda.
---

## Datos para ejecucion del workflow
El workflow debe ser ejecutado pasando como comando otro archivo con los siguientes datos:
- Nombre: Nombre del modulo que desea refactorizar
- Problema: Descripcion del motivo por el que se desea refactorizar el modulo
- resultado esperado: que resultado se espera alcanzar a traves de la refactorizacion.
- detalles adicionales: otras informaciones que sean de valor para la refactorizacion, como pueden ser librerias, formatos, tecnologias, etc. 

si faltara alguna de esta informacion, no proseguir con el workflow.

## paso 1
hacer un discovery del modulo actual a refactorizar

## paso 2 
Se debe ejecutar el workflow #quinotospec.create-proposal.md con los datos de ejecucion del workflow + discovery
