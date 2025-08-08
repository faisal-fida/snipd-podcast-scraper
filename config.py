data_dir = "data"
api_url = "https://api.snipd.com/v1"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "x-api-key": "AIzaSyDqEfh597HW-7dl2j_YxECwSjbNZ9bs93U",
}

json_data_shows = {
    "operationName": "GetTopShows",
    "variables": {
        "limit": 11,
        "offset": 0,
    },
    "query": "query GetTopShows($limit: Int, $offset: Int) {\n  top_listened_shows(\n    limit: $limit\n    offset: $offset\n    order_by: {show_rank_overall: asc}\n  ) {\n    show {\n      ...Show\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment Show on shows {\n  id\n  title\n  description\n  author\n  image_url\n  is_public\n  always_show_ai\n  is_video_public\n  __typename\n}",
}

json_data_episodes = {
    "operationName": "GetShowEpisodes",
    "variables": {
        "id": "3dc564e5-e8f7-4f72-a598-79498f162e8b",
        "limit": 11,
        "offset": 0,
    },
    "query": "query GetShowEpisodes($id: uuid!, $limit: Int, $offset: Int) {\n  episodes: episodes(\n    where: {show_id: {_eq: $id}, show: {is_public: {_eq: true}}, tomb_ts: {_is_null: true}}\n    order_by: {publish_ts: desc}\n    limit: $limit\n    offset: $offset\n  ) {\n    ...Episode\n    __typename\n  }\n}\n\nfragment Episode on episodes {\n  id\n  title\n  description\n  description_html\n  image_url\n  audio_url\n  duration_seconds\n  publish_ts\n  website\n  always_show_ai\n  show {\n    ...Show\n    __typename\n  }\n  audio_informations {\n    version\n    __typename\n  }\n  has_ai_summary: ai_summary {\n    id: episode_id\n    __typename\n  }\n  ai_description {\n    description\n    __typename\n  }\n  speakers {\n    entity_person {\n      ...EntityPerson\n      __typename\n    }\n    __typename\n  }\n  hosts {\n    person {\n      ...EntityPerson\n      __typename\n    }\n    __typename\n  }\n  mentioned_resources {\n    book {\n      ...EntityBook\n      __typename\n    }\n    __typename\n  }\n  snip_count_per_episode {\n    cnt_snips\n    __typename\n  }\n  video {\n    video_manifest_url\n    video_cover_url\n    __typename\n  }\n  __typename\n}\n\nfragment Show on shows {\n  id\n  title\n  description\n  author\n  image_url\n  is_public\n  always_show_ai\n  is_video_public\n  __typename\n}\n\nfragment EntityPerson on entity_people {\n  person_id\n  name\n  bio\n  image_url\n  stats {\n    episode_count\n    total_snips\n    total_snipping_user\n    __typename\n  }\n  __typename\n}\n\nfragment EntityBook on entity_books {\n  book_id\n  title\n  subtitle\n  cover_image_url\n  short_description\n  description\n  authors {\n    person {\n      ...EntityPerson\n      __typename\n    }\n    __typename\n  }\n  first_publish_year\n  stats {\n    snips_count\n    mentioned_episodes_count\n    mentioned_shows_count\n    rank\n    __typename\n  }\n  __typename\n}",
}


json_data_episode_by_id = {
    "operationName": "GetEpisodeById",
    "variables": {
        "id": "c6682d8f-8999-412a-91d6-a4b427d123fb",
    },
    "query": "query GetEpisodeById($id: uuid!) {\n  episode: episodes(where: {id: {_eq: $id}, tomb_ts: {_is_null: true}}) {\n    ...EpisodeWithChapters\n    __typename\n  }\n}\n\nfragment EpisodeWithChapters on episodes {\n  ...Episode\n  chapters(order_by: {start_time_seconds: asc_nulls_last}) {\n    ...Chapter\n    __typename\n  }\n  ai_summary {\n    ...EpisodeSummary\n    __typename\n  }\n  ai_description {\n    id: episode_id\n    description\n    __typename\n  }\n  episode_base_ai_note_items {\n    ...EpisdeoAiNoteItem\n    __typename\n  }\n  ai_snips {\n    ...AiSnip\n    __typename\n  }\n  __typename\n}\n\nfragment Episode on episodes {\n  id\n  title\n  description\n  description_html\n  image_url\n  audio_url\n  duration_seconds\n  publish_ts\n  website\n  always_show_ai\n  show {\n    ...Show\n    __typename\n  }\n  audio_informations {\n    version\n    __typename\n  }\n  has_ai_summary: ai_summary {\n    id: episode_id\n    __typename\n  }\n  ai_description {\n    description\n    __typename\n  }\n  speakers {\n    entity_person {\n      ...EntityPerson\n      __typename\n    }\n    __typename\n  }\n  hosts {\n    person {\n      ...EntityPerson\n      __typename\n    }\n    __typename\n  }\n  mentioned_resources {\n    book {\n      ...EntityBook\n      __typename\n    }\n    __typename\n  }\n  snip_count_per_episode {\n    cnt_snips\n    __typename\n  }\n  video {\n    video_manifest_url\n    video_cover_url\n    __typename\n  }\n  __typename\n}\n\nfragment Show on shows {\n  id\n  title\n  description\n  author\n  image_url\n  is_public\n  always_show_ai\n  is_video_public\n  __typename\n}\n\nfragment EntityPerson on entity_people {\n  person_id\n  name\n  bio\n  image_url\n  stats {\n    episode_count\n    total_snips\n    total_snipping_user\n    __typename\n  }\n  __typename\n}\n\nfragment EntityBook on entity_books {\n  book_id\n  title\n  subtitle\n  cover_image_url\n  short_description\n  description\n  authors {\n    person {\n      ...EntityPerson\n      __typename\n    }\n    __typename\n  }\n  first_publish_year\n  stats {\n    snips_count\n    mentioned_episodes_count\n    mentioned_shows_count\n    rank\n    __typename\n  }\n  __typename\n}\n\nfragment Chapter on chapters {\n  ...ChapterFields\n  episode {\n    ...Episode\n    __typename\n  }\n  __typename\n}\n\nfragment ChapterFields on chapters {\n  id: chapter_id\n  chapter_id\n  title\n  summary\n  start_time_seconds\n  end_time_seconds\n  episode {\n    ...Episode\n    __typename\n  }\n  __typename\n}\n\nfragment EpisodeSummary on episode_ai_summaries {\n  create_ts\n  preview_caption\n  preview_text\n  summaries\n  takeaways\n  id: episode_id\n  audio_summary {\n    duration_seconds\n    audio_url\n    __typename\n  }\n  __typename\n}\n\nfragment EpisdeoAiNoteItem on episode_base_ai_note_items {\n  item_id\n  episode_id\n  note_type\n  create_ts\n  body_md\n  quote\n  quote_context\n  quote_speaker_name\n  quote_start_time\n  start_time\n  end_time\n  __typename\n}\n\nfragment AiSnip on ai_snips {\n  ai_snip_id\n  episode_id\n  ai_snip_type\n  note_type\n  create_ts\n  body_md\n  quote\n  quote_context\n  quote_speaker_name\n  quote_start_time\n  start_time\n  end_time\n  __typename\n}",
}
