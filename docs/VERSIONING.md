# Versioning Policy

This project follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html): `MAJOR.MINOR.PATCH`.

## What each number means here

| Part | Increment when |
|---|---|
| `MAJOR` | A breaking change to CLI flags, JSON output shape, MCP tool signatures, or exit codes |
| `MINOR` | New CLI flags, new supported AWS services, new MCP tools, new output formats — backward compatible |
| `PATCH` | Bug fixes, parser corrections, doc updates, dependency bumps — no behavior change |

## Breaking change examples (MAJOR)

- Removing or renaming a CLI flag
- Changing an exit code meaning
- Changing a field name in `--json` or `--format agent` output
- Changing an MCP tool name or its response schema
- Dropping a Python version from the support matrix

## Non-breaking examples (MINOR)

- Adding a new `--flag`
- Adding a new AWS service parser
- Adding a new MCP tool
- Adding a new safety level (if existing levels are unchanged)

## Pre-1.0 policy

While the version is `0.x.y`, MINOR increments may include breaking changes. Once `1.0.0` is tagged, the rules above are strict.

## Tagging

Releases are tagged as `vMAJOR.MINOR.PATCH` (e.g. `v0.1.0`).

```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

The version string in `pyproject.toml` must match the tag before tagging.
