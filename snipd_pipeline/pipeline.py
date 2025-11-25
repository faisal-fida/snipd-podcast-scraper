import asyncio
import logging
import os
import time
from typing import Any, Dict, List

from snipd_pipeline.config import data_dir
from snipd_pipeline.persistence import CheckpointManager, DataSaver
from snipd_pipeline.snipd_api import SnipdAPI


State = Dict[str, Any]


class SnipdPipeline:
    def __init__(self) -> None:
        self.snipd_api = SnipdAPI()
        self.data_saver = DataSaver(data_dir)
        self.checkpoint = CheckpointManager(os.path.join(data_dir, "checkpoint.json"))
        self.checkpoint._tail_truncate_partial_line(data_dir)

    def _save(self, state: State, **updates: Any) -> None:
        """
        Update the state and save it to the checkpoint
        """
        state.update(updates)
        self.checkpoint.save(state)

    async def _fetch_top_shows(self, state: State) -> List[Dict[str, Any]]:
        """
        Fetch top shows from Snipd API
        """
        logging.info("Getting top shows")
        shows = await self.snipd_api.get_top_shows(limit=30000, offset=0)
        if not state.get("top_shows_saved", False):
            self.data_saver.save_top_shows(shows)
            self._save(state, top_shows_saved=True)
        return shows

    async def _process_episode(
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
        start_ts = time.perf_counter()
        try:
            episode_by_id = await self.snipd_api.get_episode_by_id(
                episode_id=episode_id
            )
            elapsed = (time.perf_counter() - start_ts) * 1000.0
            logging.info(
                f"Episode fetched id={episode_id} show={show_id} idx={episode_index} t_ms={elapsed:.1f}"
            )
            self.data_saver.append_episodes(episode_by_id)
            self._save(
                state,
                current_show_id=show_id,
                show_index=show_index,
                episode_index=episode_index + 1,
            )
            return True
        except Exception as exc:  # noqa: BLE001
            elapsed = (time.perf_counter() - start_ts) * 1000.0
            logging.exception(
                f"Failed processing episode id={episode_id} show={show_id} idx={episode_index} t_ms={elapsed:.1f}: {exc}"
            )
            self._save(
                state,
                current_show_id=show_id,
                show_index=show_index,
                episode_index=episode_index,
            )
            return False

    async def _process_show(
        self, top_shows: List[Dict[str, Any]], show_index: int, state: State
    ) -> bool:
        """
        Process the podcast show by id and save it to the data saver
        """
        show = top_shows[show_index].get("show", {})
        show_id = show.get("id")
        logging.info(f"Getting episodes for show: {show.get('title', '<unknown>')}")

        episodes = await self.snipd_api.get_episodes(
            show_id=show_id, limit=5000, offset=0
        )

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

        # Process episodes sequentially or with bounded concurrency (preserving ordered writes)
        async def _run_sequential() -> bool:
            for episode_index in range(start, len(episodes)):
                if not await self._process_episode(
                    show_id, show_index, episode_index, episodes, state
                ):
                    return False
            return True

        async def _run_concurrent(max_in_flight: int) -> bool:
            sem = asyncio.Semaphore(max_in_flight)

            async def worker(idx: int) -> bool:
                async with sem:
                    return await self._process_episode(
                        show_id, show_index, idx, episodes, state
                    )

            tasks = [asyncio.create_task(worker(i)) for i in range(start, len(episodes))]
            for t in tasks:
                ok = await t
                if not ok:
                    for pending in tasks:
                        if not pending.done():
                            pending.cancel()
                    return False
            return True

        from snipd_pipeline import config as _cfg
        if getattr(_cfg, "concurrency_enabled", False):
            max_in_flight = int(getattr(_cfg, "max_in_flight_episode_requests", 10) or 10)
            if not await _run_concurrent(max_in_flight):
                return False
        else:
            if not await _run_sequential():
                return False

        # Finished all episodes for this show; advance to next show
        self._save(
            state, current_show_id=None, show_index=show_index + 1, episode_index=0
        )
        return True

    async def run_async(self) -> None:
        """
        Run the pipeline asynchronously
        """
        state: State = self.checkpoint.load()
        try:
            top_shows = await self._fetch_top_shows(state)
            logging.info("Getting episodes")

            start_show_index = min(state.get("show_index", 0), len(top_shows))
            for show_index in range(start_show_index, len(top_shows)):
                if not await self._process_show(top_shows, show_index, state):
                    return
        finally:
            await self.snipd_api.close()

    def run(self) -> None:
        """
        Synchronous entrypoint to maintain existing interface
        """
        asyncio.run(self.run_async())
