import os
from pathlib import Path
from config import MEDIA_PATH

SUBTITLE_EXTENSIONS = {'.srt', '.sub', '.ass', '.ssa', '.vtt'}
VIDEO_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.mov', '.m4v'}

def scan_missing_subtitles() -> list[dict]:
    """Scan media library and return files missing subtitles."""
    missing = []
    media_path = Path(MEDIA_PATH)

    for video_file in media_path.rglob('*'):
        if video_file.suffix.lower() not in VIDEO_EXTENSIONS:
            continue

        siblings = list(video_file.parent.glob(f"{video_file.stem}*"))
        has_subtitle = any(
            f.suffix.lower() in SUBTITLE_EXTENSIONS for f in siblings
        )

        if not has_subtitle:
            missing.append({
                "path": str(video_file),
                "filename": video_file.name,
                "parent": str(video_file.parent),
                "stem": video_file.stem
            })

    return missing


if __name__ == "__main__":
    results = scan_missing_subtitles()
    print(f"Found {len(results)} files missing subtitles")
    for r in results[:5]:
        print(r['filename'])