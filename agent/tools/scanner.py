import re
from pathlib import Path
from config import MEDIA_PATH

VIDEO_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.mov', '.m4v'}

# TRaSH-standard patterns
# TV:    Show Name (Year) - S01E01 - Episode Title.mkv
# Movie: Movie Title (Year).mkv
TRASH_TV_PATTERN = re.compile(
    r'^.+\(\d{4}\)\s-\sS\d{2}E\d{2}\s-\s.+$'
)
TRASH_MOVIE_PATTERN = re.compile(
    r'^.+\(\d{4}\)$'
)


def is_well_named(filepath: Path) -> bool:
    """Return True if the file already matches TRaSH naming convention."""
    stem = filepath.stem  # filename without extension

    if TRASH_TV_PATTERN.match(stem):
        return True
    if TRASH_MOVIE_PATTERN.match(stem):
        return True

    return False


def scan_badly_named() -> list[dict]:
    """Scan media library and return video files that don't match TRaSH naming."""
    badly_named = []
    media_path = Path(MEDIA_PATH)

    if not media_path.exists():
        print(f"[Scanner] Warning: MEDIA_PATH does not exist: {MEDIA_PATH}")
        return []

    for video_file in media_path.rglob('*'):
        if video_file.suffix.lower() not in VIDEO_EXTENSIONS:
            continue

        if not is_well_named(video_file):
            badly_named.append({
                "path": str(video_file),
                "filename": video_file.name,
                "parent": str(video_file.parent),
                "stem": video_file.stem
            })

    return badly_named


if __name__ == "__main__":
    results = scan_badly_named()
    print(f"Found {len(results)} badly named files")
    for r in results[:10]:
        print(f"  {r['filename']}")