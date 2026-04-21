from pathlib import Path
from babelfish import Language
from subliminal import download_best_subtitles, save_subtitles, scan_video


def download_subtitle(video_path: str, language: str = "eng") -> dict:
    """Download best subtitle for a video file."""
    path = Path(video_path)

    if not path.exists():
        return {"success": False, "reason": "File not found"}

    try:
        video = scan_video(str(path))
        subtitles = download_best_subtitles(
            [video],
            {Language(language)}
        )

        if subtitles.get(video):
            save_subtitles(video, subtitles[video])
            return {
                "success": True,
                "path": str(path),
                "subtitle": str(subtitles[video][0])
            }
        else:
            return {"success": False, "reason": "No subtitles found"}

    except Exception as e:
        return {"success": False, "reason": str(e)}


if __name__ == "__main__":
    result = download_subtitle("/tmp/test.mkv")
    print(result)