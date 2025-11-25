CRUSH.md — Quick ops + style guide for agents

Build / install
- Python: 3.12 (pyproject) but CI tests 3.10–3.11; keep code 3.10-compatible.
- Install with uv (fast) or pip:
  - uv: uv venv .venv && . .venv/bin/activate && uv pip install -e . || uv pip install -r requirements.txt
  - pip: python -m venv .venv && . .venv/bin/activate && pip install -e . || pip install -r requirements.txt

Lint / static checks
- Ruff (CI uses ruff==0.5.5): ruff check .
- Syntax check: python -m compileall -q .
- Format (if desired): ruff format .

Run
- Entry point: python main.py

Testing
- No tests in repo yet; recommended pytest layout: tests/ with test_*.py
- Example commands (once tests exist):
  - Run all: pytest -q
  - Single file: pytest -q tests/test_pipeline.py
  - Single test: pytest -q tests/test_pipeline.py::TestPipeline::test_run

Code style guidelines
- Imports: standard lib, third-party, local; avoid wildcard; prefer explicit from ... import name; group with blank lines.
- Formatting: ruff format (black-compatible); line length 120; trailing commas for multiline structures.
- Types: use typing for public functions; enable from __future__ import annotations where needed; prefer TypedDict/Protocol over dict/Any.
- Naming: snake_case for functions/vars, PascalCase for classes, UPPER_CASE for constants; module-level constants in config.py.
- Errors: fail fast with explicit exceptions; never swallow; wrap external I/O with informative messages; log at INFO for progress and WARNING/ERROR for failures.
- Async: aiohttp sessions are long-lived; ensure await/close; keep pipeline.run() sync wrapper over async internals.
- I/O: use atomic writes for checkpoints (os.replace) and append-only JSONL for episodes; avoid partial writes.
- Data: deterministic CSV/JSON overwrites; JSONL append-only; validate shapes before write.
- Security: do not log secrets/keys; headers configurable via config.py.

Repo/automation notes
- CI runs ruff and compile checks only; keep code lint-clean locally before PR.
- If Cursor/Copilot rules files are added later (.cursor/rules/, .cursorrules, .github/copilot-instructions.md), mirror key rules here.
