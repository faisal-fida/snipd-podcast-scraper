## Snipd Podcast Data Pipeline

An end‑to‑end, resumeable data pipeline that ingests podcast metadata from the Snipd public API, persists it reliably, and is production‑ready for long‑running collection jobs. Designed for clarity, robustness, and maintainability — ideal to showcase in a portfolio or resume.

### Highlights
- **Resumeable checkpointing**: Safely restarts from the last processed show/episode after any failure or interruption.
- **Robust persistence**: Deterministic CSV/JSON for shows; append‑only JSONL for episodes to support large datasets and partial writes.
- **Modular architecture**: Clean separation of concerns (`pipeline`, `persistence`, `snipd_api`, `config`).
- **Simple operational model**: One command to run; sensible defaults; clear logs.

### What it does
- Fetches top podcast shows from Snipd and saves them to `data/top_shows.csv` and `data/top_shows.json`.
- Iterates every top show to fetch episodes, then fetches each episode by id and writes one JSON document per line to `data/episodes.jsonl`.
- Records progress in `data/checkpoint.json` after each episode and after finishing each show, so re‑running continues where it left off.

## Architecture

```mermaid
flowchart TD
    A[main.py] --> B[SnipdPipeline.run()]
    B --> C[SnipdAPI]
    B --> D[DataSaver]
    B --> E[CheckpointManager]

    C -->|GraphQL| F[(Snipd Public API)]
    D -->|CSV/JSON/JSONL| G[(data/)]
    E -->|atomic write| G
```

### Key modules
- `main.py`: Minimal entry point that instantiates and runs the pipeline.
- `pipeline.py`: Orchestrates the end‑to‑end flow with clear, testable methods.
- `persistence.py`: Reliable persistence layer (`DataSaver`) and resume system (`CheckpointManager`).
- `snipd_api.py`: Thin API client for Snipd GraphQL endpoints.
- `config.py`: Centralized configuration (API URL, headers, GraphQL queries, data directory).

## Quickstart

### Prerequisites
- Python 3.10+
- pip (and optionally venv/conda for isolation)

### Install
```bash
python -m venv .venv
. .venv/bin/activate   # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### Run
```bash
python main.py
```

First run will create the `data/` directory (if missing) and start collecting.

## Data outputs
- `data/top_shows.csv`: Tabular export of top shows (deterministic overwrite).
- `data/top_shows.json`: JSON array of top shows (deterministic overwrite).
- `data/episodes.jsonl`: Append‑only JSON Lines; one episode object per line.
- `data/checkpoint.json`: Internal progress state (safe to delete to restart from scratch).

Example JSONL line (single episode document):
```json
{"id":"...","title":"...","publish_ts":"...", "show": {"id":"...","title":"..."}}
```

## Configuration
Edit `config.py` to adjust:
- `data_dir`: Output directory (default `data`).
- `api_url`, `headers`: Snipd API base and headers. Replace `x-api-key` if you have your own key.
- GraphQL payloads: `json_data_shows`, `json_data_episodes`, `json_data_episode_by_id`.

Tuning the fetch sizes (defaults in code):
- Top shows: limit=30000, offset=0
- Episodes per show: limit=5000, offset=0

## Operational behavior
- The pipeline logs progress at INFO level. Adjust via `logging.basicConfig(level=logging.INFO)` in `main.py`.
- If interrupted or if an exception occurs, re‑running resumes from the last saved checkpoint.
- To restart from scratch, delete `data/checkpoint.json` and rerun.

## Project structure
```
snipd/
  ├─ config.py              # Configuration and GraphQL queries
  ├─ main.py                # Minimal entrypoint
  ├─ pipeline.py            # SnipdPipeline orchestration
  ├─ persistence.py         # DataSaver + CheckpointManager + atomic I/O
  ├─ snipd_api.py           # Snipd GraphQL client
  └─ data/                  # Outputs (created at runtime)
     ├─ top_shows.csv
     ├─ top_shows.json
     ├─ episodes.jsonl
     └─ checkpoint.json
```

## Why this is resume‑friendly and robust
- **Checkpoint granularity**: Saves indices at show and episode level; work after a crash is minimal.
- **Atomic writes**: Uses temp files and `os.replace` for checkpoint writes to avoid corruption.
- **Append‑only episodes**: JSONL format is ideal for large streams and is resilient to partial writes.
- **Separation of concerns**: Fetching, persistence, and orchestration are decoupled for testability and maintenance.

## Extensibility roadmap
- CLI flags (e.g., `--reset`, `--limit`, `--offset`, `--resume-from`).
- Backoff, retries, and HTTP timeouts per endpoint.
- Idempotency/deduplication safeguards for episodes.
- Parallelism by show or by episode batch with backpressure and rate‑limit awareness.
- Structured logging and metrics (e.g., OpenTelemetry).

## Considerations
- External API availability, schema, and rate limits may affect throughput.
- Headers include a sample `x-api-key`; replace with a proper key if required by Snipd.
- This project is for educational/demo purposes; respect API terms of service and data usage policies.

## Contributing
Issues and PRs are welcome. Please include a clear description, reproduction steps, and tests where appropriate.

## License
Add your preferred license (e.g., MIT) to the repository root as `LICENSE`.

## Contact
If you have questions or would like to discuss this project, feel free to reach out.


