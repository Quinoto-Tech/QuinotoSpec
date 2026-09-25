# Ejemplo TDD — Python

## RED

```python
import pytest

from src.billing import calculate_total


def test_calculate_total_applies_discount():
    assert calculate_total(100, discount=10) == 90
```

```bash
pytest -q tests/test_billing.py::test_calculate_total_applies_discount
```

Resultado esperado: falla porque `calculate_total` no está definido o no aplica el descuento.

## GREEN

```python
def calculate_total(subtotal: int, discount: int = 0) -> int:
    return subtotal - discount
```

```bash
pytest -q tests/test_billing.py::test_calculate_total_applies_discount
```

Resultado esperado: pasa.

## REFACTOR

```python
def calculate_total(subtotal: int, discount: int = 0) -> int:
    if discount < 0:
        raise ValueError("discount must be non-negative")
    return subtotal - discount
```

```bash
pytest -q tests/test_billing.py
pytest -q
```

La nueva validación también debe tener un test que observe `ValueError` antes de declarar la refactorización terminada.
