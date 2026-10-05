# Makefile

The `Makefile` has three targets, all marked `.PHONY`, so they always run as commands rather than being treated as files to build.

```make
verify-setup:
	@python --version
	@python -c "import fastapi, pydantic, httpx, pytest, schemathesis; assert pydantic.VERSION.startswith('2'), 'Pydantic v2 required'; print('packages OK')"
	@claude --version
	@test -s setup/claude-answer.md || (echo 'MISSING: setup/claude-answer.md (A0 step 6)'; exit 1)
	@pytest -q tests/test_smoke.py

test:
	pytest -q

lint-contract:
	python tools/lint_contract.py docs/openapi.yaml
```

## `make verify-setup`

Checks that the environment is ready. The `@` prefix hides each command so only its output is shown.

1. Prints the Python version.
2. Imports `fastapi`, `pydantic`, `httpx`, `pytest` and `schemathesis`, checks that Pydantic is v2, then prints `packages OK`.
3. Prints the Claude Code CLI version, which confirms `claude` is installed.
4. Checks that `setup/claude-answer.md` exists and isn't empty. If it's missing, prints `MISSING: setup/claude-answer.md (A0 step 6)` and stops.
5. Runs the smoke tests in `tests/test_smoke.py`.

## `make test`

Runs `pytest -q`, which runs every test pytest finds. Currently that is the two smoke tests in `tests/test_smoke.py`:

- `test_openapi_document_can_be_loaded`: `docs/openapi.yaml` parses, is OpenAPI 3.x, and defines at least one path.
- `test_participant_files_are_present`: the required repo files (`.claude/settings.json`, `.devcontainer/devcontainer.json`, `CLAUDE.md`, `Makefile`, `tracker/CR-2.md`, `tracker/README.md`) exist.

## `make lint-contract`

Runs `tools/lint_contract.py` on `docs/openapi.yaml` to check the API contract. Run it whenever the contract changes.
