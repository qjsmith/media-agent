import requests
from config import TMDB_API_KEY

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_TIMEOUT = 10  # seconds


def search_tmdb(title: str, media_type: str = "tv") -> list[dict]:
    """Search TMDB for a show or movie by title."""
    url = f"{TMDB_BASE_URL}/search/{media_type}"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title
    }
    try:
        response = requests.get(url, params=params, timeout=TMDB_TIMEOUT)
        if response.status_code != 200:
            return []
        results = response.json().get("results", [])
        return [
            {
                "id": r.get("id"),
                "title": r.get("name") or r.get("title"),
                "year": (r.get("first_air_date") or r.get("release_date") or "")[:4],
                "popularity": r.get("popularity"),
                "overview": r.get("overview")
            }
            for r in results[:5]
        ]
    except requests.exceptions.RequestException as e:
        print(f"  [TMDB] search_tmdb error: {e}")
        return []


def get_episode_details(show_id: int, season: int, episode: int) -> dict:
    """Get specific episode details from TMDB."""
    url = f"{TMDB_BASE_URL}/tv/{show_id}/season/{season}/episode/{episode}"
    params = {"api_key": TMDB_API_KEY}
    try:
        response = requests.get(url, params=params, timeout=TMDB_TIMEOUT)
        if response.status_code != 200:
            return {}
        data = response.json()
        return {
            "title": data.get("name"),
            "overview": data.get("overview"),
            "air_date": data.get("air_date"),
            "season": season,
            "episode": episode
        }
    except requests.exceptions.RequestException as e:
        print(f"  [TMDB] get_episode_details error: {e}")
        return {}


def search_episode_by_title(show_id: int, season: int, episode_title: str) -> dict:
    """Search for an episode by title within a season using fuzzy matching."""
    url = f"{TMDB_BASE_URL}/tv/{show_id}/season/{season}"
    params = {"api_key": TMDB_API_KEY}
    try:
        response = requests.get(url, params=params, timeout=TMDB_TIMEOUT)
        if response.status_code != 200:
            return {}
        episodes = response.json().get("episodes", [])
        if not episodes:
            return {}

        from thefuzz import fuzz
        best_score = 0
        best_episode = {}
        for ep in episodes:
            ep_name = ep.get("name", "")
            score = max(
                fuzz.token_sort_ratio(episode_title.lower(), ep_name.lower()),
                fuzz.ratio(episode_title.lower(), ep_name.lower())
            )
            if score > best_score:
                best_score = score
                best_episode = ep

        if best_score >= 80:
            return {
                "title": best_episode.get("name"),
                "episode_number": best_episode.get("episode_number"),
                "season": season,
                "overview": best_episode.get("overview"),
                "air_date": best_episode.get("air_date")
            }
        return {}

    except requests.exceptions.RequestException as e:
        print(f"  [TMDB] search_episode_by_title error: {e}")
        return {}


if __name__ == "__main__":
    results = search_tmdb("Breaking Bad")
    for r in results:
        print(r)