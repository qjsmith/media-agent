from thefuzz import fuzz

from agent.tools.metadata import search_tmdb


def score_match(parsed: dict, candidate: dict) -> float:
    """Score how well a TMDB candidate matches parsed file info."""
    score = 0.0
    weights = 0.0

    title_score = 0.0

    if parsed["cleaned_title"] and candidate["title"]:
        title_score = max(
            fuzz.token_sort_ratio(parsed["cleaned_title"].lower(), candidate["title"].lower()),
            fuzz.ratio(parsed["cleaned_title"].lower(), candidate["title"].lower()),
        )
        score += title_score * 0.6
        weights += 0.6

    if parsed["year"] and candidate["year"]:
        if str(parsed["year"]) == str(candidate["year"]):
            score += 100 * 0.3
        else:
            score += 0 * 0.3
        weights += 0.3

    if candidate.get("popularity", 0) > 0:
        pop_score = min(candidate["popularity"] / 100 * 100, 100)
        pop_weight = 0.3 if not parsed["year"] else 0.1
        score += pop_score * pop_weight
        weights += pop_weight

    if weights == 0:
        return 0.0

    raw_score = round(score / weights, 2)

    if title_score >= 95 and not parsed["year"]:
        raw_score = max(raw_score, 90.0)

    return raw_score


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
            "reason": "no_title_parsed",
            "candidates": [],
        }

    candidates = search_tmdb(parsed["cleaned_title"], media_type)

    if not candidates:
        return {
            "match": None,
            "score": 0.0,
            "ambiguous": False,
            "unidentifiable": True,
            "reason": "tmdb_no_candidates",
            "candidates": [],
        }

    scored = []
    for candidate in candidates:
        s = score_match(parsed, candidate)
        scored.append({"candidate": candidate, "score": s})

    scored.sort(key=lambda x: x["score"], reverse=True)

    best = scored[0]
    second = scored[1] if len(scored) > 1 else None

    # Only flag as ambiguous if scores are close AND title isn't a near-perfect match
    ambiguous = False
    if second and (best["score"] - second["score"]) < 25:
        best_title_score = max(
            fuzz.token_sort_ratio(parsed["cleaned_title"].lower(), best["candidate"]["title"].lower()),
            fuzz.ratio(parsed["cleaned_title"].lower(), best["candidate"]["title"].lower()),
        )
        if best_title_score < 95:
            ambiguous = True

    return {
        "match": best["candidate"],
        "score": best["score"],
        "ambiguous": ambiguous,
        "unidentifiable": False,
        "reason": None,
        "candidates": [s["candidate"] for s in scored[:3]],
    }
