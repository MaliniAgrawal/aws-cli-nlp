# Release Notes Template

Copy this block and prepend it to `CHANGELOG.md` for each release.
Replace all `<!-- -->` placeholders. Delete sections that have no entries.

---

```markdown
## [X.Y.Z] — YYYY-MM-DD

One-sentence summary of what this release is about.

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 

### Security
- 

[X.Y.Z]: https://github.com/MaliniAgrawal/aws-cli-nlp/compare/vPREV...vX.Y.Z
```

---

## Checklist before tagging

- [ ] Version in `pyproject.toml` matches the new tag
- [ ] CHANGELOG.md entry is written and dated
- [ ] All tests pass: `python -m pytest -q`
- [ ] All linters clean: `black --check . && isort --check-only . && flake8`
- [ ] `pip install -e .` works from a clean venv
- [ ] Entry point smoke test: `aws-nlp "list s3 buckets"`

## Tagging

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

See [docs/VERSIONING.md](VERSIONING.md) for what constitutes a MAJOR / MINOR / PATCH change.
