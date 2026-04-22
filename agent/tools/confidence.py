from thefuzz import fuzz
from agent.tools.metadata import search_tmdb
from agent.tools.parser import parse_filename


def score_match(parsed: dict, candidate: dict) -> float:
    """Score how well a TMDB candidate matches parsed file info."""
    score = 0.0
    weights = 0.0

    # Title match — most important factor
    if parsed["cleaned_title"] and candidate["title"]:
        title_score = max(
            fuzz.token_sort_ratio(
                parsed["cleaned_title"].lower(),
                candidate["title"].lower()
            ),
            fuzz.ratio(
                parsed["cleaned_title"].lower(),
                candidate["title"].lower()
            )
        )
        score += title_score * 0.6
        weights += 0.6

    # Year match
    if parsed["year"] and candidate["year"]:
        if str(parsed["year"]) == str(candidate["year"]):
            score += 100 * 0.3
        else:
            score += 0 * 0.3
        weights += 0.3

    # Popularity boost — weighted higher when no year available
    if candidate.get("popularity", 0) > 0:
        pop_score = min(candidate["popularity"] / 100 * 100, 100)
        pop_weight = 0.3 if not parsed["year"] else 0.1
        score += pop_score * pop_weight
        weights += pop_weight

    if weights == 0:
        return 0.0

    return round(score / weights, 2)


def get_best_match(parsed: dict, media_type: str = "tv") -> dict:
    """
    Search TMDB and return the best match with confidence score.
    Returns dict with match info and whether it's ambiguous.
    """
    if not parsed["cleaned_title"]:
        return {
            "match": None,
            "score": 0.0,
            "ambiguous": False,
            "unidentifiable": True,
            "candidates": []
        }

    candidates = search_tmdb(parsed["cleaned_title"], media_type)

    if not candidates:
        return {
            "match": None,
            "score": 0.0,
            "ambiguous": False,
            "unidentifiable": True,
            "candidates": []
        }

    # Score all candidates
    scored = []
    for candidate in candidates:
        s = score_match(parsed, candidate)
        scored.append({"candidate": candidate, "score": s})

    scored.sort(key=lambda x: x["score"], reverse=True)

    best = scored[0]
    second = scored[1] if len(scored) > 1 else None

    # Check for ambiguity — top two results are too close
    ambiguous = False
    if second and (best["score"] - second["score"]) < 25:
        ambiguous = True

    return {
        "match": best["candidate"],
        "score": best["score"],
        "ambiguous": ambiguous,
        "unidentifiable": False,
        "candidates": [s["candidate"] for s in scored[:3]]
    }

if __name__ == "__main__":
    test_cases = [
        ("Breaking.Bad.S01E03.720p.BluRay.mkv", "/mnt/media/TV Shows/Breaking.Bad.S01E03.720p.BluRay.mkv", "tv"),
        ("avatar.2009.1080p.mkv", "/mnt/media/Movies/avatar.2009.1080p.mkv", "movie"),
        ("S02E03.mkv", "/mnt/media/TV Shows/The Office/Season 2/S02E03.mkv", "tv"),
    ]

    for name, path, media_type in test_cases:
        parsed = parse_filename(path)
        result = get_best_match(parsed, media_type)
        print(f"\nFile: {name}")
        print(f"  Match: {result['match']['title'] if result['match'] else 'None'}")
        print(f"  Score: {result['score']}")
        print(f"  Ambiguous: {result['ambiguous']}")
        print(f"  Unidentifiable: {result['unidentifiable']}")