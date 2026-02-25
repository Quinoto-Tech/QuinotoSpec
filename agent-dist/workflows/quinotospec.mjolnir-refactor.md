---
description: Flujo para generar una Propuesta de Refactor "Mjolnir" que reescribe módulos enteros bajo demanda.
---

## Datos para ejecucion del workflow
El workflow debe ser ejecutado pasando como comando otro archivo con los siguientes datos:
- Nombre: Nombre del modulo que desea refactorizar
- Problema: Descripcion del motivo por el que se desea refactorizar el modulo
- resultado esperado: que resultado se espera alcanzar a traves de la refactorizacion.
- detalles adicionales: otras informaciones que sean de valor para la refactorizacion, como pueden ser librerias, formatos, tecnologias, etc. 

### si faltara alguna de esta informacion, no proseguir con el workflow.

## paso 1
genera un archivo con el nombre .quinoto-spec/{nombre_del_modulo_a_refactorizar}/mjolnir-refactor.yml con los Datos para ejecucion del workflow (pedir verificacion humana)

## paso 2
- hacer un discovery del modulo actual a refactorizar de la misma manera que se realiza con /quinotospec.discovery pero dejar los archivos en .quinotospec/{nombre_del_modulo_a_refactorizar}
- el archivo 07-product-and-agreements.md generalo con su contenido que sea relevante para el contexto.

## paso 3 
- Se debe ejecutar el workflow #quinotospec.create-proposal.md con los archivos generados en el discovery discovery + Datos para ejecucion del workflow (archivo yml generado en el paso 1)
