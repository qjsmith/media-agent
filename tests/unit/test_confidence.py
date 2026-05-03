from unittest.mock import patch

from agent.tools.confidence import get_best_match, score_match

# ---------------------------------------------------------------------------
# Helpers — fake TMDB candidates so we never hit the API
# ---------------------------------------------------------------------------


def make_candidate(title, year=None, popularity=50):
    return {
        "id": 1,
        "title": title,
        "year": str(year) if year else None,
        "popularity": popularity,
    }


def make_parsed(title, year=None):
    return {
        "cleaned_title": title,
        "year": year,
        "season": None,
        "episode": None,
        "filename": f"{title}.mkv",
        "context": {"parent_folder": "", "grandparent_folder": ""},
    }


# ---------------------------------------------------------------------------
# score_match
# ---------------------------------------------------------------------------


def test_exact_title_match_high_score():
    parsed = make_parsed("Breaking Bad", year=2008)
    candidate = make_candidate("Breaking Bad", year=2008)
    score = score_match(parsed, candidate)
    assert score >= 90


def test_exact_title_wrong_year_lower_score():
    parsed = make_parsed("Breaking Bad", year=2008)
    candidate = make_candidate("Breaking Bad", year=2015)
    score = score_match(parsed, candidate)
    assert score < 90


def test_different_title_low_score():
    parsed = make_parsed("Breaking Bad", year=2008)
    candidate = make_candidate("The Office", year=2005)
    score = score_match(parsed, candidate)
    assert score < 50


def test_no_year_high_title_match_still_confident():
    # A 95%+ title match with no year should still hit 90
    parsed = make_parsed("Breaking Bad", year=None)
    candidate = make_candidate("Breaking Bad", year=2008, popularity=80)
    score = score_match(parsed, candidate)
    assert score >= 90


def test_popularity_boost_when_no_year():
    # Higher popularity should score better when no year available
    parsed = make_parsed("The Office", year=None)
    low_pop = make_candidate("The Office", year=2005, popularity=10)
    high_pop = make_candidate("The Office", year=2005, popularity=200)
    assert score_match(parsed, high_pop) >= score_match(parsed, low_pop)


# ---------------------------------------------------------------------------
# get_best_match — with mocked candidates (monkeypatching search_tmdb)
# ---------------------------------------------------------------------------


def test_get_best_match_no_title_returns_unidentifiable():
    parsed = make_parsed(None)
    result = get_best_match(parsed, "tv")
    assert result["unidentifiable"] is True
    assert result["match"] is None


def test_get_best_match_empty_title_returns_unidentifiable():
    parsed = make_parsed("")
    result = get_best_match(parsed, "tv")
    assert result["unidentifiable"] is True


def test_get_best_match_with_mock(monkeypatch):
    candidates = [
        make_candidate("Breaking Bad", year=2008, popularity=100),
        make_candidate("Breaking Point", year=2010, popularity=5),
    ]
    monkeypatch.setattr("agent.tools.confidence.search_tmdb", lambda title, media_type: candidates)

    parsed = make_parsed("Breaking Bad", year=2008)
    result = get_best_match(parsed, "tv")

    assert result["unidentifiable"] is False
    assert result["match"]["title"] == "Breaking Bad"
    assert result["score"] >= 90
    assert result["ambiguous"] is False


def test_get_best_match_ambiguous_when_scores_close(monkeypatch):
    # Two very similar titles, no year — should be flagged ambiguous
    candidates = [
        make_candidate("The Office US", year=None, popularity=50),
        make_candidate("The Office UK", year=None, popularity=45),
    ]
    monkeypatch.setattr("agent.tools.confidence.search_tmdb", lambda title, media_type: candidates)

    parsed = make_parsed("The Office", year=None)
    result = get_best_match(parsed, "tv")
    assert result["ambiguous"] is True


def test_get_best_match_no_title_reason():
    parsed = {"cleaned_title": "", "year": None}
    result = get_best_match(parsed)
    assert result["reason"] == "no_title_parsed"


def test_get_best_match_no_candidates_reason():
    parsed = {"cleaned_title": "Some Obscure Title", "year": None}
    with patch("agent.tools.confidence.search_tmdb", return_value=[]):
        result = get_best_match(parsed)
    assert result["reason"] == "tmdb_no_candidates"
