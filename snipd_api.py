import requests
from config import (
    api_url,
    headers,
    json_data_shows,
    json_data_episodes,
    json_data_episode_by_id,
)


class SnipdAPI:
    def __init__(self):
        self.headers = headers
        self.api_url = api_url

    def get_top_shows(self, limit: int, offset: int):
        """
        Get top podcast shows from Snipd API
        """
        json_data_shows["variables"]["limit"] = limit
        json_data_shows["variables"]["offset"] = offset
        response = requests.post(
            f"{self.api_url}/public/graphql", headers=self.headers, json=json_data_shows
        )
        return response.json()["data"]["top_listened_shows"]

    def get_episodes(self, show_id: str, limit: int, offset: int):
        """
        Get episodes for a podcast show from Snipd API
        """
        json_data_episodes["variables"]["id"] = show_id
        json_data_episodes["variables"]["limit"] = limit
        json_data_episodes["variables"]["offset"] = offset
        response = requests.post(
            f"{self.api_url}/public/graphql",
            headers=self.headers,
            json=json_data_episodes,
        )
        return response.json()["data"]["episodes"]

    def get_episode_by_id(self, episode_id: str):
        """
        Get episode by id from Snipd API
        """
        json_data_episode_by_id["variables"]["id"] = episode_id
        response = requests.post(
            f"{self.api_url}/public/graphql",
            headers=self.headers,
            json=json_data_episode_by_id,
        )
        return response.json()["data"]["episode"]
