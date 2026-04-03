# Parser Migration Guide (Function-Based to Class-Based)

This project now supports class-based parser plugins via `BaseParser` while keeping legacy function-based parsers working.

## New parser contract

Implement a parser class that inherits from `src.core.base_parser.BaseParser` and provides:

- `get_service_name()`
- `get_intents()`
- `generate_command(intent, entities)`
- `validate(intent, entities, aws_session=None)`
- `get_examples()`

## Migration steps for each remaining parser

1. Keep your existing `SERVICE_NAME`, `INTENTS`, and `EXAMPLES` constants.
2. Create `<Service>Parser(BaseParser)` and move your current `generate_command` and `validate` logic into class methods.
3. Add `get_service_name`, `get_intents`, and `get_examples` methods.
4. Keep module-level wrapper functions for compatibility:
   - `generate_command(...)`
   - `validate(...)`
   - `get_service()` returns `parser_instance.to_service_dict()`
5. Run unit tests for that service parser plus command-generation integration tests.

## Discovery behavior

`src/core/registry.py` now loads parsers in this order:

1. Class-based parser (`BaseParser` subclass) from `src.parsers.<service>.parser`
2. Legacy fallback (`SERVICE_NAME` + `get_service()`) for untouched parsers

This allows incremental migration service-by-service.

## Reference implementations

- `src/parsers/s3/parser.py`
- `src/parsers/rds/parser.py`
