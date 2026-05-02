from pathlib import Path

from agent.tools.scanner import is_well_named

# ---------------------------------------------------------------------------
# TV shows — well named (should return True)
# ---------------------------------------------------------------------------


def test_well_named_tv():
    assert is_well_named(Path("Breaking Bad (2008) - S01E03 - ...And the Bag's in the River.mkv")) is True


def test_well_named_tv_simple():
    assert is_well_named(Path("The Office (2005) - S02E03 - The Dundies.mkv")) is True


# ---------------------------------------------------------------------------
# Movies — well named (should return True)
# ---------------------------------------------------------------------------


def test_well_named_movie():
    assert is_well_named(Path("Whiplash (2014).mkv")) is True


def test_well_named_movie_long_title():
    assert is_well_named(Path("The Grand Budapest Hotel (2014).mkv")) is True


# ---------------------------------------------------------------------------
# Badly named (should return False)
# ---------------------------------------------------------------------------


def test_badly_named_dots():
    assert is_well_named(Path("Breaking.Bad.S01E03.720p.BluRay.mkv")) is False


def test_badly_named_no_year():
    assert is_well_named(Path("Breaking Bad - S01E03 - Some Episode.mkv")) is False


def test_badly_named_movie_no_year():
    assert is_well_named(Path("Whiplash.2014.1080p.BluRay.mkv")) is False


def test_badly_named_bare_episode():
    assert is_well_named(Path("S02E03.mkv")) is False


def test_badly_named_brackets():
    assert is_well_named(Path("[pseudo] Rick and Morty S01E02 Lawnmower Dog.mkv")) is False
