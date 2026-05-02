"""
Integration tests — these hit the real TMDB API.
Run locally only, not in CI.

    pytest tests/integration/
"""

from agent.tools.metadata import search_episode_by_title, search_tmdb


def test_search_tmdb_breaking_bad():
    results = search_tmdb("Breaking Bad", "tv")
    assert len(results) > 0
    titles = [r["title"] for r in results]
    assert any("Breaking Bad" in t for t in titles)


def test_search_tmdb_movie():
    results = search_tmdb("Whiplash", "movie")
    assert len(results) > 0
    assert results[0]["title"] == "Whiplash"


def test_search_episode_by_title_simpsons():
    results = search_tmdb("The Simpsons", "tv")
    assert results
    show_id = results[0]["id"]
    ep = search_episode_by_title(show_id, 5, "Cape Feare")
    assert ep is not None
    assert ep["episode_number"] == 2


def test_search_episode_by_title_homer_goes_to_college():
    results = search_tmdb("The Simpsons", "tv")
    show_id = results[0]["id"]
    ep = search_episode_by_title(show_id, 5, "Homer Goes To College")
    assert ep is not None
    assert ep["episode_number"] == 3


def test_search_episode_by_title_no_season():
    # IT Crowd has no Season 5 on TMDB — should return empty
    results = search_tmdb("The IT Crowd", "tv")
    assert results
    show_id = results[0]["id"]
    ep = search_episode_by_title(show_id, 5, "The Internet Is Coming")
    assert ep is None or ep == {}
