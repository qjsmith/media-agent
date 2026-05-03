from unittest.mock import MagicMock

from agent.tools.llm import llm_resolve


def make_llm(response_text):
    """Helper — returns a mock LLM that responds with response_text."""
    llm = MagicMock()
    llm.invoke.return_value = MagicMock(content=response_text)
    return llm


CANDIDATES = [
    {"title": "The Office", "year": 2005, "popularity": 95.0},
    {"title": "The Office UK", "year": 2001, "popularity": 40.0},
]

PARSED = {
    "filename": "The.Office.S03E05.mkv",
    "cleaned_title": "The Office",
    "season": 3,
    "episode": 5,
    "year": None,
    "context": {
        "parent_folder": "Season 3",
        "grandparent_folder": "The Office",
    },
}


def test_llm_returns_correct_candidate():
    llm = make_llm("The Office (2005)")
    result = llm_resolve(PARSED, CANDIDATES, llm)
    assert result is not None
    assert result["title"] == "The Office"
    assert result["year"] == 2005


def test_llm_returns_none_on_unknown():
    llm = make_llm("UNKNOWN")
    result = llm_resolve(PARSED, CANDIDATES, llm)
    assert result is None


def test_llm_returns_none_on_unrecognized_response():
    llm = make_llm("Seinfeld (1989)")
    result = llm_resolve(PARSED, CANDIDATES, llm)
    assert result is None


def test_llm_picks_second_candidate():
    llm = make_llm("The Office UK (2001)")
    result = llm_resolve(PARSED, CANDIDATES, llm)
    assert result is not None
    assert result["title"] == "The Office UK"
