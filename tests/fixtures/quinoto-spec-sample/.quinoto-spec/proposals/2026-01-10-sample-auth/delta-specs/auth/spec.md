# Delta Spec: auth — sample-auth

> **Propuesta:** Sample Auth JWT
> **Prefijo:** AUTH-a1b2
> **Fecha:** 2026-01-10
> **Estado**: 🟢 En Curso

---

## ADDED Requirements

### Requirement: Two-Factor Authentication
The system SHALL support TOTP-based two-factor authentication for user login.

#### Scenario: successful TOTP verification
- **GIVEN** a user with 2FA enabled
- **WHEN** they submit a valid TOTP code
- **THEN** access is granted

### Requirement: Recovery Codes
The system SHALL generate 10 single-use recovery codes when 2FA is activated.

---

## MODIFIED Requirements

(sin cambios — no existe `specs/auth/spec.md` previo)

---

## REMOVED Requirements

(sin cambios)

---

## RENAMED Requirements

(sin cambios)
