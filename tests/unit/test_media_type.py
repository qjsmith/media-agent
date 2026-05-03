from agent.tools.media_type import detect_media_type


def make_parsed(season=None, episode=None, path="", parent="", grandparent="", is_movie_special=False):
    """Helper — builds a minimal parsed dict."""
    return {
        "season": season,
        "episode": episode,
        "original_path": path,
        "is_movie_special": is_movie_special,
        "context": {
            "parent_folder": parent,
            "grandparent_folder": grandparent,
        },
    }


def test_movie_special_returns_movie():
    parsed = make_parsed(is_movie_special=True)
    assert detect_media_type(parsed) == "movie"


def test_season_present_returns_tv():
    parsed = make_parsed(season=1)
    assert detect_media_type(parsed) == "tv"


def test_episode_present_returns_tv():
    parsed = make_parsed(episode=5)
    assert detect_media_type(parsed) == "tv"


def test_movies_in_path_returns_movie():
    parsed = make_parsed(path="/mnt/media/Movies/Inception (2010)/Inception (2010).mkv")
    assert detect_media_type(parsed) == "movie"


def test_tv_shows_in_path_returns_tv():
    parsed = make_parsed(path="/mnt/media/TV Shows/The Office/Season 3/episode.mkv")
    assert detect_media_type(parsed) == "tv"


def test_movie_in_parent_folder_returns_movie():
    parsed = make_parsed(parent="movie collection")
    assert detect_media_type(parsed) == "movie"


def test_film_in_grandparent_returns_movie():
    parsed = make_parsed(grandparent="films")
    assert detect_media_type(parsed) == "movie"


def test_show_in_parent_returns_tv():
    parsed = make_parsed(parent="tv shows")
    assert detect_media_type(parsed) == "tv"


def test_no_clues_defaults_to_tv():
    parsed = make_parsed()
    assert detect_media_type(parsed) == "tv"
