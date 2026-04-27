import re
from pathlib import Path


# Matches S01E01 or 1x01 style season/episode patterns
EPISODE_PATTERN_SXE = re.compile(r'[Ss](\d{1,2})[Ee](\d{1,2})')
EPISODE_PATTERN_XY = re.compile(r'(?<!\d)(\d{1,2})[xX](\d{1,2})(?!\d)')

YEAR_PATTERN = re.compile(
    r'[\.\s\(\[]?((?:19|20)\d{2})[\.\s\)\]]?'
)

# Season-only patterns for folder names
SEASON_PATTERN_S = re.compile(r'[Ss](\d{1,2})')
SEASON_PATTERN_WORD = re.compile(r'[Ss]eason\s+(\d+)', re.IGNORECASE)
SEASON_PATTERN_LEADING = re.compile(r'^(\d+)\D')

# Movie Pattern
MOVIE_SPECIAL_PATTERN = re.compile(r'[Ss](\d{1,2})[Mm](\d{1,2})')

JUNK_WORDS = {
    'bluray', 'blu-ray', 'webrip', 'webdl', 'web-dl', 'hdtv', 'dvdrip',
    'xvid', 'x264', 'x265', 'h264', 'h265', 'aac', 'mp3', 'dts', 'ac3',
    'rarbg', 'yify', 'proper', 'repack', 'extended', 'theatrical',
    '1080p', '720p', '480p', '2160p', '4k', 'hdr', 'uhd', 'remux',
    'complete', 'season', 'episode', 'final', 'v2', 'v3', 'mp4'
}

USELESS_FOLDERS = {'media', 'tv shows', 'movies', 'tv', 'films', 'video'}

QUALITY_PATTERNS = {
    "resolution": re.compile(r'\b(480p|720p|1080p|2160p|4k|uhd)\b', re.IGNORECASE),
    "source": re.compile(r'\b(bluray|blu-ray|webrip|webdl|web-dl|hdtv|dvdrip|remux)\b', re.IGNORECASE),
    "codec": re.compile(r'\b(x264|x265|h264|h265|xvid)\b', re.IGNORECASE),
    "audio": re.compile(r'\b(aac|mp3|dts|ac3|atmos|truehd)\b', re.IGNORECASE),
}


def find_episode(text: str):
    """
    Try to find season/episode in text.
    Returns (match, season, episode) or (None, None, None).
    Prefers SxE format over NxN format.
    """
    m = EPISODE_PATTERN_SXE.search(text)
    if m:
        return m, int(m.group(1)), int(m.group(2))

    m = EPISODE_PATTERN_XY.search(text)
    if m:
        return m, int(m.group(1)), int(m.group(2))

    return None, None, None


def extract_season_from_folder(folder: str) -> int | None:
    """
    Try to extract a season number from a folder name.
    Tries S01 style, then Season N style, then leading digit style.
    """
    # S01 style — but only if no episode number follows (avoid matching S01E01)
    m = SEASON_PATTERN_S.search(folder)
    if m and not EPISODE_PATTERN_SXE.search(folder):
        return int(m.group(1))

    # Season N style
    m = SEASON_PATTERN_WORD.search(folder)
    if m:
        return int(m.group(1))

    # Leading digit(s) — e.g. "5The Simpsons - Season Five"
    m = SEASON_PATTERN_LEADING.match(folder)
    if m:
        return int(m.group(1))

    return None


def extract_show_name_from_folder(folder: str) -> str | None:
    """
    Try to extract a clean show name from a folder name by stripping
    season info, junk words, and quality tags.
    """
    # Strip leading digits (Simpsons style)
    name = re.sub(r'^\d+', '', folder)
    # Strip S01 style tags and everything after
    name = re.sub(r'[Ss]\d{2}.*$', '', name)
    # Strip written-out season names e.g. "- Season Five"
    name = re.sub(r'\s*-\s*Season\s+\w+.*$', '', name, flags=re.IGNORECASE)
    # Strip "Season N" and everything after
    name = re.sub(r'[Ss]eason\s+\d+.*$', '', name, flags=re.IGNORECASE)
    # Strip quality tags
    name = re.sub(r'\b(480p|720p|1080p|2160p|4k|uhd|bluray|webrip|webdl|web-dl|hdtv|dvdrip|x264|x265|h264|h265|mp4)\b.*$', '', name, flags=re.IGNORECASE)
    # Strip year in parentheses e.g. "Whiplash (2014)" → "Whiplash"
    name = re.sub(r'\s*[\(\[](19|20)\d{2}[\)\]]\s*', '', name).strip()
    # Normalize dots, dashes, underscores
    name = re.sub(r'[._]', ' ', name)
    name = re.sub(r'\s*-\s*$', '', name)
    name = name.strip()

    if len(name) < 2 or name.lower() in USELESS_FOLDERS:
        return None

    return name


def extract_quality_info(filename: str) -> dict:
    """Extract quality metadata from filename."""
    quality = {}
    for key, pattern in QUALITY_PATTERNS.items():
        match = pattern.search(filename)
        if match:
            quality[key] = match.group(1).lower()
    return quality


def clean_title(raw: str) -> str:
    """Remove junk words and normalize a raw title string."""
    title = re.sub(r'[._]', ' ', raw)
    # Strip leading bracket if filename starts with one e.g. [Rick.and.Morty...]
    title = re.sub(r'^\s*[\[\(]', '', title)
    title = re.sub(r'[\[\(].*?[\]\)]', '', title)
    title = re.sub(r'[\(\[]?(19|20)\d{2}[\)\]]?', '', title)
    words = [w for w in title.split() if w.lower() not in JUNK_WORDS]
    return ' '.join(words).strip()


def clean_episode_title(raw: str) -> str:
    """Clean a filename for use as an episode title — strips quality tags but keeps common words."""
    title = re.sub(r'[._]', ' ', raw)
    title = re.sub(r'[\[\(].*?[\]\)]', '', title)
    title = re.sub(r'\b(19|20)\d{2}\b', '', title)
    # Only strip quality/technical words, not common english words
    quality_junk = {
        'bluray', 'blu-ray', 'webrip', 'webdl', 'web-dl', 'hdtv', 'dvdrip',
        'xvid', 'x264', 'x265', 'h264', 'h265', 'aac', 'mp3', 'dts', 'ac3',
        'rarbg', 'yify', 'proper', 'repack', '1080p', '720p', '480p',
        '2160p', '4k', 'hdr', 'uhd', 'remux', 'v2', 'v3'
    }
    words = [w for w in title.split() if w.lower() not in quality_junk]
    return ' '.join(words).strip()


def parse_filename(filepath: str) -> dict:
    """
    Extract as much info as possible from a filepath.
    Uses filename + parent folder + grandparent folder as context.
    Falls back to folder context when filename has no season/episode info.
    """
    path = Path(filepath)
    filename = path.stem
    parent = path.parent.name
    grandparent = path.parent.parent.name

    result = {
        "original_path": filepath,
        "filename": path.name,
        "season": None,
        "episode": None,
        "year": None,
        "raw_title": None,
        "cleaned_title": None,
        "episode_title": None,
        "quality": {},
        "context": {
            "parent_folder": parent,
            "grandparent_folder": grandparent
        }
    }

    # Try to find season/episode in filename first, then parent folder
    ep_match, season, episode = find_episode(filename)
    if not ep_match:
        ep_match, season, episode = find_episode(parent)

    if ep_match:
        result["season"] = season
        result["episode"] = episode

    # Check for movie special format e.g. S05M01
    movie_special_match = MOVIE_SPECIAL_PATTERN.search(filename)
    if movie_special_match:
        result["is_movie_special"] = True
        before = filename[:movie_special_match.start()].strip().rstrip('-_ ')
        after = filename[movie_special_match.end():].strip().lstrip('-_ ')
        # Combine show name + movie title e.g. "Steven Universe The Movie"
        full_title = f"{before} {after}".strip() if after else before
        result["cleaned_title"] = clean_title(full_title) if full_title else None
        result["episode_title"] = None
    else:
        result["is_movie_special"] = False

    # Try to find year
    year_match = YEAR_PATTERN.search(filename) or YEAR_PATTERN.search(parent)
    if year_match:
        result["year"] = int(year_match.group(1))

    # Extract raw title - everything before the season/episode marker
    if ep_match:
        raw = filename[:ep_match.start()].strip().rstrip('[](). -')
    else:
        raw = filename

    # Clean the title
    cleaned = clean_title(raw)

    # If we have no season/episode from filename or parent, try folder fallback
    if result["season"] is None and not result.get("is_movie_special"):
        # Try parent folder for season
        season_from_parent = extract_season_from_folder(parent)
        if season_from_parent:
            result["season"] = season_from_parent

        # Try grandparent folder for season if parent didn't have it
        if result["season"] is None:
            season_from_grandparent = extract_season_from_folder(grandparent)
            if season_from_grandparent:
                result["season"] = season_from_grandparent

        # If parent is just "Season N", show name is in grandparent
        if SEASON_PATTERN_WORD.match(parent.strip()):
            show_name = extract_show_name_from_folder(grandparent)
        else:
            show_name = extract_show_name_from_folder(parent) or extract_show_name_from_folder(grandparent)

        if show_name:
            cleaned = show_name
            # The filename itself is the episode title in this case
            raw_episode_title = clean_episode_title(filename)
            # Strip the show name from the front if it's there
            # e.g. "The Simpsons - Lisa's Sax" → "Lisa's Sax"
            if raw_episode_title.lower().startswith(show_name.lower()):
                raw_episode_title = raw_episode_title[len(show_name):].lstrip(' -')
            result["episode_title"] = raw_episode_title

    # Final fallback if still empty
    if not cleaned or len(cleaned) < 2:
        parent_cleaned = clean_title(parent)
        grandparent_cleaned = clean_title(grandparent)
        if parent_cleaned.lower() not in USELESS_FOLDERS and len(parent_cleaned) > 2:
            cleaned = parent_cleaned
        elif grandparent_cleaned.lower() not in USELESS_FOLDERS and len(grandparent_cleaned) > 2:
            cleaned = grandparent_cleaned
        else:
            cleaned = None

    result["raw_title"] = raw.strip().rstrip('[](). -')
    if not result.get("is_movie_special"):
        result["cleaned_title"] = cleaned
    result["quality"] = extract_quality_info(filename)

    return result


if __name__ == "__main__":
    test_cases = [
        "/mnt/media/TV Shows/Breaking.Bad.S01E03.720p.BluRay.mkv",
        "/mnt/media/TV Shows/The Office/Season 2/S02E03.mkv",
        "/mnt/media/Movies/avatar.2009.1080p.mkv",
        "/mnt/media/TV Shows/rarbg_final_v2.mkv",
        "/mnt/media/TV Shows/The Simpsons/Season 10/The Simpsons [10x12] Sunday Cruddy Sunday.avi",
        "/mnt/media/TV Shows/The Simpsons/5The Simpsons - Season Five/Cape Feare.mp4",
        "/mnt/media/TV Shows/BoJack Horseman/Season 1/Some Episode.mkv",
        "/mnt/media/TV Shows/Abbott Elementary/Abbott Elementary Season 2/Some Episode.mkv",
        "/mnt/media/TV Shows/Arcane/Arcane.S01.1080p.WEBRip.x265/Some Episode.mkv",
        "/mnt/media/TV Shows/The Simpsons/5The Simpsons - Season Five/Cape Feare.mp4",
    ]

    for path in test_cases:
        result = parse_filename(path)
        print(f"\nFile: {result['filename']}")
        print(f"  Title: {result['cleaned_title']}")
        print(f"  Season: {result['season']} Episode: {result['episode']}")
        print(f"  Episode Title: {result['episode_title']}")
        print(f"  Year: {result['year']}")
        print(f"  Quality: {result['quality']}")