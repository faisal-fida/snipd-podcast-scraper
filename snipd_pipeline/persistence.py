import json
import os
from typing import Any, Dict, List

import pandas as pd


def ensure_dir(path: str) -> None:
    """
    Ensure the directory exists
    """
    os.makedirs(path, exist_ok=True)


def atomic_write_json(path: str, payload: Dict[str, Any]) -> None:
    """
    Atomic write a JSON file with a rolling .bak backup.
    """
    tmp_path = f"{path}.tmp"
    bak_path = f"{path}.bak"
    with open(tmp_path, "w", encoding="utf-8") as tmp_file:
        json.dump(payload, tmp_file, ensure_ascii=False, indent=2)
    try:
        if os.path.exists(path):
            try:
                if os.path.exists(bak_path):
                    os.remove(bak_path)
            except Exception:
                pass
            try:
                os.replace(path, bak_path)
            except Exception:
                pass
    except Exception:
        pass
    os.replace(tmp_path, path)


class CheckpointManager:
    def __init__(self, checkpoint_path: str) -> None:
        self.checkpoint_path = checkpoint_path

    def _tail_truncate_partial_line(self, episodes_dir: str) -> None:
        base = os.path.join(episodes_dir, "episodes")
        idx = 1
        last_existing = None
        while True:
            path = f"{base}-{idx:05d}.jsonl"
            if os.path.exists(path):
                last_existing = path
                idx += 1
            else:
                break
        if not last_existing:
            return
        try:
            with open(last_existing, "rb") as f:
                try:
                    f.seek(-2048, os.SEEK_END)
                    tail = f.read().decode("utf-8", errors="ignore")
                except OSError:
                    f.seek(0)
                    tail = f.read().decode("utf-8", errors="ignore")
            if tail and not tail.endswith("\n"):
                with open(last_existing, "rb+") as f:
                    f.seek(0, os.SEEK_END)
                    end_pos = f.tell()
                    # truncate back to last newline
                    backtrack = min(2048, end_pos)
                    f.seek(-backtrack, os.SEEK_END)
                    data = f.read().decode("utf-8", errors="ignore")
                    cut = data.rfind("\n")
                    if cut != -1:
                        f.truncate(end_pos - (backtrack - (cut + 1)))
        except Exception:
            pass

    def load(self) -> Dict[str, Any]:
        """
        Load the checkpoint with fallback to .bak if the main file is corrupt.
        """
        candidates = [self.checkpoint_path, f"{self.checkpoint_path}.bak"]
        for path in candidates:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    data.setdefault("show_index", 0)
                    data.setdefault("episode_index", 0)
                    data.setdefault("current_show_id", None)
                    data.setdefault("top_shows_saved", False)
                    return data
                except Exception:
                    continue
        return {
            "version": 1,
            "show_index": 0,
            "episode_index": 0,
            "current_show_id": None,
            "top_shows_saved": False,
        }

    def save(self, state: Dict[str, Any]) -> None:
        """
        Save the checkpoint
        """
        ensure_dir(os.path.dirname(self.checkpoint_path))
        atomic_write_json(self.checkpoint_path, state)


class DataSaver:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        ensure_dir(self.data_dir)
        self._shard_prefix = "episodes"
        self._shard_ext = ".jsonl"
        self._max_shard_bytes = 100 * 1024 * 1024  # 100MB default

    def save_top_shows(self, data: List[Dict[str, Any]]) -> None:
        """
        Save the top shows
        """
        shows: List[Dict[str, Any]] = []
        for entry in data:
            show_obj = entry.get("show") if isinstance(entry, dict) else None
            if show_obj:
                show_obj = {k: v for k, v in show_obj.items() if k != "__typename"}
                shows.append(show_obj)

        if not shows:
            return

        df = pd.DataFrame(shows)
        csv_path = os.path.join(self.data_dir, "top_shows.csv")
        json_path = os.path.join(self.data_dir, "top_shows.json")

        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        with open(json_path, "w", encoding="utf-8-sig") as f:
            json.dump(shows, f, ensure_ascii=False, indent=2)

    def _current_shard_path(self) -> str:
        base = os.path.join(self.data_dir, f"{self._shard_prefix}")
        # Find the highest-numbered shard that exists; if none, start at 00001
        idx = 1
        while True:
            path = f"{base}-{idx:05d}{self._shard_ext}"
            if not os.path.exists(path):
                # If no shard yet and idx==1, return first shard path
                if idx == 1:
                    return path
                # Otherwise return previous existing shard path for appends
                return f"{base}-{idx-1:05d}{self._shard_ext}"
            idx += 1

    def _rotate_if_needed(self, path: str) -> str:
        try:
            size = os.path.getsize(path)
        except OSError:
            size = 0
        if size >= self._max_shard_bytes:
            # Create next shard path
            base = os.path.join(self.data_dir, f"{self._shard_prefix}")
            # Extract current index
            name = os.path.basename(path)
            try:
                current_idx = int(name.split("-")[-1].split(".")[0])
            except Exception:
                current_idx = 1
            next_path = f"{base}-{current_idx+1:05d}{self._shard_ext}"
            return next_path
        return path

    def append_episodes(self, data: Any) -> None:
        """
        Append episodes to the data saver (sharded JSONL)
        """
        episodes: List[Dict[str, Any]] = []
        if isinstance(data, list):
            episodes = data
        elif isinstance(data, dict):
            episodes = [data]
        else:
            return

        shard_path = self._current_shard_path()
        shard_path = self._rotate_if_needed(shard_path)
        ensure_dir(self.data_dir)
        with open(shard_path, "a", encoding="utf-8-sig") as f:
            for ep in episodes:
                if isinstance(ep, dict) and "__typename" in ep:
                    ep = {k: v for k, v in ep.items() if k != "__typename"}
                f.write(json.dumps(ep, ensure_ascii=False) + "\n")
