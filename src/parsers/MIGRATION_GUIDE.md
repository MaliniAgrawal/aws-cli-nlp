# Parser Migration Guide: Function Modules → Class Plugins

This project now supports a class-based plugin architecture via `BaseParser`.

## New contract

Create a parser class that inherits from `src.core.base_parser.BaseParser` and implement:

- `get_service_name()`
- `get_intents()`
- `generate_command(intent, entities)`
- `validate(intent, entities, aws_session=None)`
- `get_examples()`

## Minimal migration steps for each parser

1. Keep existing module constants (`SERVICE_NAME`, `INTENTS`, optionally `EXAMPLES`).
2. Move existing `generate_command` and `validate` logic into class methods.
3. Add module singleton:
   - `_PARSER = YourParser()`
   - `get_parser() -> BaseParser`
4. Keep compatibility wrappers so existing imports/tests continue to work:
   - `generate_command(...)` delegates to `_PARSER.generate_command(...)`
   - `validate(...)` delegates to `_PARSER.validate(...)`
   - `get_service()` returns legacy service dict and includes `parser` / `examples`
5. Do **not** change folder layout or remove `manifest.json`.

## Example skeleton

```python
from src.core.base_parser import BaseParser

class ExampleParser(BaseParser):
    def get_service_name(self):
        return SERVICE_NAME

    def get_intents(self):
        return INTENTS

    def get_examples(self):
        return EXAMPLES

    def generate_command(self, intent, entities):
        ...

    def validate(self, intent, entities, aws_session=None):
        ...

_PARSER = ExampleParser()

def get_parser():
    return _PARSER

# Backwards-compatible wrappers

def generate_command(intent, entities):
    return _PARSER.generate_command(intent, entities)

def validate(intent, entities, aws_session=None):
    return _PARSER.validate(intent, entities, aws_session=aws_session)

def get_service():
    return {
        "name": _PARSER.get_service_name(),
        "intents": _PARSER.get_intents(),
        "generate_command": generate_command,
        "validate": validate,
        "examples": _PARSER.get_examples(),
        "parser": _PARSER,
    }
```

## Registry behavior

`src/core/registry.py` now prefers `get_parser()` (class-based), and falls back to legacy `SERVICE_NAME` + `get_service()` modules when needed.
