from agent.tools.renamer import build_tv_path, build_movie_path, sanitize


# ---------------------------------------------------------------------------
# sanitize
# ---------------------------------------------------------------------------

def test_sanitize_removes_colon():
    assert ":" not in sanitize("Breaking Bad: Season 1")

def test_sanitize_removes_slash():
    assert "/" not in sanitize("AC/DC")

def test_sanitize_clean_string_unchanged():
    assert sanitize("Breaking Bad") == "Breaking Bad"


# ---------------------------------------------------------------------------
# build_tv_path
# ---------------------------------------------------------------------------

def test_build_tv_path_standard():
    path = build_tv_path(
        base_path="/mnt/media/TV Shows",
        show_title="Breaking Bad",
        show_year=2008,
        season=1,
        episode=3,
        episode_title="And the Bag's in the River",
        extension=".mkv",
    )
    assert "Breaking Bad (2008)" in path
    assert "Season 01" in path
    assert "S01E03" in path
    assert path.endswith(".mkv")

def test_build_tv_path_double_digit_season():
    path = build_tv_path(
        base_path="/mnt/media/TV Shows",
        show_title="The Simpsons",
        show_year=1989,
        season=10,
        episode=12,
        episode_title="Sunday Cruddy Sunday",
        extension=".avi",
    )
    assert "Season 10" in path
    assert "S10E12" in path

def test_build_tv_path_structure():
    path = build_tv_path(
        base_path="/mnt/media/TV Shows",
        show_title="Severance",
        show_year=2022,
        season=1,
        episode=4,
        episode_title="The You You Are",
        extension=".mkv",
    )
    parts = path.split("/")
    # Should be: /mnt/media/TV Shows / Show (Year) / Season XX / filename
    assert parts[-3] == "Severance (2022)"
    assert parts[-2] == "Season 01"
    assert parts[-1].endswith(".mkv")


# ---------------------------------------------------------------------------
# build_movie_path
# ---------------------------------------------------------------------------

def test_build_movie_path_standard():
    path = build_movie_path(
        base_path="/mnt/media/Movies",
        movie_title="Whiplash",
        movie_year=2014,
        extension=".mp4",
    )
    assert "Whiplash (2014)" in path
    assert path.endswith(".mp4")

def test_build_movie_path_structure():
    path = build_movie_path(
        base_path="/mnt/media/Movies",
        movie_title="The Grand Budapest Hotel",
        movie_year=2014,
        extension=".mkv",
    )
    parts = path.split("/")
    # Should be: /mnt/media/Movies / Movie (Year) / Movie (Year).mkv
    assert parts[-2] == "The Grand Budapest Hotel (2014)"
    assert parts[-1] == "The Grand Budapest Hotel (2014).mkv"

def test_build_movie_path_folder_and_filename_match():
    path = build_movie_path(
        base_path="/mnt/media/Movies",
        movie_title="Avatar",
        movie_year=2009,
        extension=".mkv",
    )
    parts = path.split("/")
    assert parts[-2] == parts[-1].replace(".mkv", "")
