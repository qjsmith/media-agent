import re
from pathlib import Path


# Matches S01E01 or 1x01 style season/episode patterns
EPISODE_PATTERN_SXE = re.compile(r'[Ss](\d{1,2})[Ee](\d{1,2})')
EPISODE_PATTERN_XY = re.compile(r'(?<!\d)(\d{1,2})[xX](\d{1,2})(?!\d)')

YEAR_PATTERN = re.compile(
    r'[\.\s\(\[]?((?:19|20)\d{2})[\.\s\)\]]?'
)

JUNK_WORDS = {
    'bluray', 'blu-ray', 'webrip', 'webdl', 'web-dl', 'hdtv', 'dvdrip',
    'xvid', 'x264', 'x265', 'h264', 'h265', 'aac', 'mp3', 'dts', 'ac3',
    'rarbg', 'yify', 'proper', 'repack', 'extended', 'theatrical',
    '1080p', '720p', '480p', '2160p', '4k', 'hdr', 'uhd', 'remux',
    'complete', 'season', 'episode', 'final', 'v2', 'v3'
}

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
    title = re.sub(r'[\[\(].*?[\]\)]', '', title)
    # Remove year
    title = re.sub(r'\b(19|20)\d{2}\b', '', title)
    words = [w for w in title.split() if w.lower() not in JUNK_WORDS]
    return ' '.join(words).strip()


def parse_filename(filepath: str) -> dict:
    """
    Extract as much info as possible from a filepath.
    Uses filename + parent folder + grandparent folder as context.
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

    # Try to find year
    year_match = YEAR_PATTERN.search(filename) or YEAR_PATTERN.search(parent)
    if year_match:
        result["year"] = int(year_match.group(1))

    # Extract raw title - everything before the season/episode marker
    if ep_match:
        raw = filename[:ep_match.start()].strip().rstrip('[](). -')
    else:
        raw = filename

    # If raw title is too short or empty, try parent folder
    cleaned = clean_title(raw)
    USELESS_FOLDERS = {'media', 'tv shows', 'movies', 'tv', 'films', 'video'}
    if len(cleaned) < 2:
        parent_cleaned = clean_title(parent)
        grandparent_cleaned = clean_title(grandparent)
        if parent_cleaned.lower() not in USELESS_FOLDERS and len(parent_cleaned) > 2:
            cleaned = parent_cleaned
        elif grandparent_cleaned.lower() not in USELESS_FOLDERS and len(grandparent_cleaned) > 2:
            cleaned = grandparent_cleaned
        else:
            cleaned = None

    result["raw_title"] = raw.strip().rstrip('[](). -')
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
        "/mnt/media/TV Shows/The Simpsons/Season 9/Girly Edition.avi",
    ]

    for path in test_cases:
        result = parse_filename(path)
        print(f"\nFile: {result['filename']}")
        print(f"  Title: {result['cleaned_title']}")
        print(f"  Season: {result['season']} Episode: {result['episode']}")
        print(f"  Year: {result['year']}")
        print(f"  Quality: {result['quality']}")
        print(f"  Context: {result['context']}")