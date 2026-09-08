# User Stories (Sample Auth JWT)

| ID | User Story | Criterios de Aceptación | Prioridad | Estimación | Servicio |
| --- | --- | --- | --- | --- | --- |
| US-AUTH-a1b2-001 | Como **usuario**, quiero **activar 2FA con TOTP desde mi perfil**, para **proteger mi cuenta con un segundo factor**. | - Puedo escanear un QR para vincular mi app TOTP<br>- Puedo desactivar 2FA con confirmación de contraseña | P1 | M | auth-service |
| US-AUTH-a1b2-002 | Como **administrador**, quiero **que 2FA sea obligatorio para roles admin**, para **reducir el riesgo de compromiso de cuentas privilegiadas**. | - El login de admin exige código TOTP válido<br>- Se bloquea el acceso tras 5 intentos fallidos | P1 | S | auth-service |
| US-AUTH-a1b2-003 | Como **usuario**, quiero **recibir códigos de recuperación de un solo uso**, para **no perder acceso si pierdo mi dispositivo TOTP**. | - Se generan 10 códigos de recuperación al activar 2FA<br>- Cada código es de un solo uso | P2 | S | notification-service |
