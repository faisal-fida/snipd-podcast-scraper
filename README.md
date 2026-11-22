# snipd-podcast-scraper

Resumable async pipeline that collects top podcast shows and full episode data (summaries, chapters, snips) from the Snipd public GraphQL API.

## Features

- Fetches top shows (`GetTopShows`), saves them to `data/top_shows.csv` and `data/top_shows.json`.
- For each show, lists its episodes, then fetches every episode by id (`GetEpisodeById`) and appends it as one JSON line to sharded files `data/episodes-00001.jsonl`, `-00002`, ... (a new shard starts at about 100 MB).
- Checkpoint in `data/checkpoint.json` (atomic write) after each episode, so a rerun continues where it stopped. A partial last line in the episode file is truncated on startup.
- `aiohttp` client with a 30 second timeout and up to 5 retries with jittered exponential backoff.
- Optional bounded concurrency for episode requests (`concurrency_enabled` in `snipd_pipeline/config.py`, off by default).

## Tech stack

Python 3.12 (see `pyproject.toml`), `aiohttp`, `pandas`.

## Structure

```
main.py                   entry point
snipd_pipeline/config.py  API URL, headers, GraphQL queries, data dir
snipd_pipeline/pipeline.py  orchestration, resume logic
snipd_pipeline/snipd_api.py async GraphQL client
snipd_pipeline/persistence.py  CSV/JSON/JSONL writers, checkpoint
```

## Setup

```bash
uv venv .venv && . .venv/bin/activate
uv pip install aiohttp pandas
# or: python -m venv .venv && . .venv/bin/activate && pip install aiohttp pandas
```

Environment variable:

| Name | Purpose |
|------|---------|
| `SNIPD_API_KEY` | Value sent as the `x-api-key` header to the Snipd GraphQL endpoint. Use the key your own Snipd web session uses; none is included in this repo. |

## Run

```bash
export SNIPD_API_KEY=...
python main.py
```

To start over, delete `data/checkpoint.json` (and the output files).

## Limitations

- Unofficial use of an undocumented API: queries, key requirements and rate limits can change or block access without notice. Check the Snipd terms before collecting data.
- The pipeline requests up to 30000 shows and 5000 episodes per show, with one request per episode, so a full run is very long.
- Sequential by default.
- `.github/workflows/ci.yml` installs from a `requirements.txt` that does not exist in the repo, so that workflow fails until one is added.
- No tests.

## License

MIT
