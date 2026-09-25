# Ejemplo TDD — TypeScript

## RED

```typescript
import { describe, expect, it } from "vitest";
import { formatUserName } from "../src/user-name";

describe("formatUserName", () => {
  it("combina nombre y apellido", () => {
    expect(formatUserName("Ada", "Lovelace")).toBe("Ada Lovelace");
  });
});
```

```bash
npm test -- --run src/user-name.test.ts
```

Resultado esperado: falla porque `formatUserName` todavía no existe o no devuelve el valor esperado.

## GREEN

```typescript
export function formatUserName(firstName: string, lastName: string): string {
  return `${firstName} ${lastName}`.trim();
}
```

```bash
npm test -- --run src/user-name.test.ts
```

Resultado esperado: pasa.

## REFACTOR

```typescript
export function formatUserName(firstName: string, lastName: string): string {
  return [firstName, lastName]
    .map((value) => value.trim())
    .filter(Boolean)
    .join(" ");
}
```

```bash
npm test -- --run src/user-name.test.ts
npm test
```

El comportamiento no cambia y la suite completa permanece en verde.
