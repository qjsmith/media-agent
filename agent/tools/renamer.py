import os
import re
from pathlib import Path
from agent.tools.metadata import get_episode_details


def sanitize(name: str) -> str:
    """Remove characters that are invalid in filenames."""
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()


def build_tv_path(
    base_path: str,
    show_title: str,
    show_year: int,
    season: int,
    episode: int,
    episode_title: str,
    extension: str
) -> str:
    """Build TRaSH-standard TV path."""
    show_folder = sanitize(f"{show_title} ({show_year})")
    season_folder = f"Season {season:02d}"
    filename = sanitize(
        f"{show_title} ({show_year}) - S{season:02d}E{episode:02d} - {episode_title}{extension}"
    )
    return str(Path(base_path) / show_folder / season_folder / filename)


def build_movie_path(
    base_path: str,
    movie_title: str,
    movie_year: int,
    extension: str
) -> str:
    """Build TRaSH-standard movie path."""
    folder = sanitize(f"{movie_title} ({movie_year})")
    filename = sanitize(f"{movie_title} ({movie_year}){extension}")
    return str(Path(base_path) / folder / filename)


def rename_file(original_path: str, new_path: str, dry_run: bool = True) -> dict:
    """
    Rename/move a file to the new path.
    dry_run=True means we log but don't actually move anything.
    """
    original = Path(original_path)
    new = Path(new_path)

    if not original.exists():
        return {"success": False, "reason": "Original file not found"}

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "original": original_path,
            "new_path": new_path,
            "reason": "Dry run — no files moved"
        }

    try:
        new.parent.mkdir(parents=True, exist_ok=True)
        original.rename(new)
        return {
            "success": True,
            "dry_run": False,
            "original": original_path,
            "new_path": new_path
        }
    except Exception as e:
        return {"success": False, "reason": str(e)}


if __name__ == "__main__":
    # Test TV path building
    tv_path = build_tv_path(
        base_path="/mnt/media/TV Shows",
        show_title="Breaking Bad",
        show_year=2008,
        season=1,
        episode=3,
        episode_title="...And the Bag's in the River",
        extension=".mkv"
    )
    print(f"TV path: {tv_path}")

    # Test movie path building
    movie_path = build_movie_path(
        base_path="/mnt/media/Movies",
        movie_title="Avatar",
        movie_year=2009,
        extension=".mkv"
    )
    print(f"Movie path: {movie_path}")