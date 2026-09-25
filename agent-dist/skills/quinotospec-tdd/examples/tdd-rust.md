# Ejemplo TDD — Rust

## RED

```rust
#[test]
fn slugifies_a_title() {
    assert_eq!(slugify("Hello World"), "hello-world");
}
```

```bash
cargo test slugifies_a_title
```

Resultado esperado: falla porque `slugify` todavía no existe o produce un valor incorrecto.

## GREEN

```rust
pub fn slugify(value: &str) -> String {
    value.to_lowercase().replace(' ', "-")
}
```

```bash
cargo test slugifies_a_title
```

Resultado esperado: pasa.

## REFACTOR

```rust
pub fn slugify(value: &str) -> String {
    value
        .chars()
        .map(|character| {
            if character.is_ascii_alphanumeric() {
                character.to_ascii_lowercase()
            } else {
                '-'
            }
        })
        .collect()
}
```

```bash
cargo test slugifies_a_title
cargo test
```

Añade casos para acentos, guiones y entradas vacías antes de cambiar el comportamiento.
