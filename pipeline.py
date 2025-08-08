import logging
import os
from typing import Any, Dict, List

from persistence import CheckpointManager, DataSaver
from snipd_api import SnipdAPI


State = Dict[str, Any]


class SnipdPipeline:
    def __init__(self, data_dir: str) -> None:
        self.snipd_api = SnipdAPI()
        self.data_saver = DataSaver(data_dir)
        self.checkpoint = CheckpointManager(os.path.join(data_dir, "checkpoint.json"))

    def _save(self, state: State, **updates: Any) -> None:
        """
        Update the state and save it to the checkpoint
        """
        state.update(updates)
        self.checkpoint.save(state)

    def _fetch_top_shows(self, state: State) -> List[Dict[str, Any]]:
        """
        Fetch top shows from Snipd API
        """
        logging.info("Getting top shows")
        shows = self.snipd_api.get_top_shows(limit=30000, offset=0)
        if not state.get("top_shows_saved", False):
            self.data_saver.save_top_shows(shows)
            self._save(state, top_shows_saved=True)
        return shows

    def _process_episode(
        self,
        show_id: str,
        show_index: int,
        episode_index: int,
        episodes: List[Dict[str, Any]],
        state: State,
    ) -> bool:
        """
        Process the podcast episode by id and save it to the data saver
        """
        episode_id = episodes[episode_index].get("id")
        logging.info(f"Getting episode by id: {episode_id}")
        try:
            episode_by_id = self.snipd_api.get_episode_by_id(episode_id=episode_id)
            self.data_saver.append_episodes(episode_by_id)
            self._save(
                state,
                current_show_id=show_id,
                show_index=show_index,
                episode_index=episode_index + 1,
            )
            return True
        except Exception as exc:  # noqa: BLE001
            logging.exception(f"Failed processing episode {episode_id}: {exc}")
            self._save(
                state,
                current_show_id=show_id,
                show_index=show_index,
                episode_index=episode_index,
            )
            return False

    def _process_show(
        self, top_shows: List[Dict[str, Any]], show_index: int, state: State
    ) -> bool:
        """
        Process the podcast show by id and save it to the data saver
        """
        show = top_shows[show_index].get("show", {})
        show_id = show.get("id")
        logging.info(f"Getting episodes for show: {show.get('title', '<unknown>')}")

        episodes = self.snipd_api.get_episodes(show_id=show_id, limit=5000, offset=0)

        # Resume from episode index if we are on the same show as the checkpoint
        start = (
            state.get("episode_index", 0)
            if state.get("current_show_id") == show_id
            else 0
        )
        if start == 0 and state.get("current_show_id") != show_id:
            self._save(
                state, current_show_id=show_id, episode_index=0, show_index=show_index
            )

        for episode_index in range(start, len(episodes)):
            if not self._process_episode(
                show_id, show_index, episode_index, episodes, state
            ):
                return False

        # Finished all episodes for this show; advance to next show
        self._save(
            state, current_show_id=None, show_index=show_index + 1, episode_index=0
        )
        return True

    def run(self) -> None:
        """
        Run the pipeline
        """
        state: State = self.checkpoint.load()
        top_shows = self._fetch_top_shows(state)
        logging.info("Getting episodes")

        start_show_index = min(state.get("show_index", 0), len(top_shows))
        for show_index in range(start_show_index, len(top_shows)):
            if not self._process_show(top_shows, show_index, state):
                return
