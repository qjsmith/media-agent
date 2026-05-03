def detect_media_type(parsed: dict) -> str:
    """Guess if file is tv or movie based on parsed info."""
    if parsed.get("is_movie_special"):
        return "movie"
    if parsed["season"] is not None or parsed["episode"] is not None:
        return "tv"

    full_path = parsed.get("original_path", "").lower()
    if "/movies/" in full_path:
        return "movie"
    if "/tv shows/" in full_path or "/tv/" in full_path:
        return "tv"

    parent = parsed["context"]["parent_folder"].lower()
    grandparent = parsed["context"]["grandparent_folder"].lower()
    if "movie" in parent or "film" in parent:
        return "movie"
    if "movie" in grandparent or "film" in grandparent:
        return "movie"
    if "tv" in parent or "show" in parent or "series" in parent:
        return "tv"
    return "tv"
