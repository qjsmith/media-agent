import requests
from config import TMDB_API_KEY

TMDB_BASE_URL = "https://api.themoviedb.org/3"

def search_tmdb(title: str, media_type: str = "tv") -> list[dict]:
    """Search TMDB for a show or movie by title."""
    url = f"{TMDB_BASE_URL}/search/{media_type}"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title
    }
    response = requests.get(url, params=params)
    
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


def get_episode_details(show_id: int, season: int, episode: int) -> dict:
    """Get specific episode details from TMDB."""
    url = f"{TMDB_BASE_URL}/tv/{show_id}/season/{season}/episode/{episode}"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params)
    
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


if __name__ == "__main__":
    results = search_tmdb("Breaking Bad")
    for r in results:
        print(r)