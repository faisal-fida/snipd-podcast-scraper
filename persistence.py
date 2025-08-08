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
    Atomic write a JSON file
    """
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as tmp_file:
        json.dump(payload, tmp_file, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


class CheckpointManager:
    def __init__(self, checkpoint_path: str) -> None:
        self.checkpoint_path = checkpoint_path

    def load(self) -> Dict[str, Any]:
        """
        Load the checkpoint
        """
        if os.path.exists(self.checkpoint_path):
            try:
                with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data.setdefault("show_index", 0)
                data.setdefault("episode_index", 0)
                data.setdefault("current_show_id", None)
                data.setdefault("top_shows_saved", False)
                return data
            except Exception:
                pass
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

    def append_episodes(self, data: Any) -> None:
        """
        Append episodes to the data saver
        """
        # Data may be a single episode dict or a list of episode dicts
        episodes: List[Dict[str, Any]] = []
        if isinstance(data, list):
            episodes = data
        elif isinstance(data, dict):
            episodes = [data]
        else:
            return

        jsonl_path = os.path.join(self.data_dir, "episodes.jsonl")
        with open(jsonl_path, "a", encoding="utf-8-sig") as f:
            for ep in episodes:
                if isinstance(ep, dict) and "__typename" in ep:
                    ep = {k: v for k, v in ep.items() if k != "__typename"}
                f.write(json.dumps(ep, ensure_ascii=False) + "\n")
