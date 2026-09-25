# Defense in depth

## Principio

Corrige la causa raíz en su capa responsable y añade defensas solo en los límites donde un valor inválido puede causar daño.

## Capas

1. **Dominio**: valida invariantes y rechaza datos imposibles.
2. **Frontera**: valida esquema, formato y permisos.
3. **Integración**: limita reintentos, timeouts y payloads.
4. **Persistencia**: usa constraints, claves y migraciones seguras.
5. **Observabilidad**: registra el contexto mínimo sin secretos.

## Reglas

- No escudas una causa raíz con más condicionales.
- Cada defensa tiene un test y un mensaje accionable.
- La validación repetida debe tener una razón de seguridad o contrato.
- Evita silenciar errores que ocultan pérdida de datos.
- Revisa defensas existentes antes de añadir otra.

## Checklist

- [ ] La causa raíz tiene una corrección propia.
- [ ] La defensa está en el límite correcto.
- [ ] El fallo se observa aunque la defensa exista.
- [ ] El test demuestra el comportamiento de la defensa.
- [ ] No se registran datos sensibles.
