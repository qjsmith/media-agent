from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from config import GROQ_API_KEY, MEDIA_PATH
from agent.tools.scanner import scan_badly_named
from agent.tools.parser import parse_filename
from agent.tools.confidence import get_best_match
from agent.tools.metadata import get_episode_details
from agent.tools.renamer import build_tv_path, build_movie_path, rename_file
from agent.tools.logger import log_decision

CONFIDENCE_THRESHOLD = 90.0
DRY_RUN = True  # Set to False when you're ready to actually rename files


def detect_media_type(parsed: dict) -> str:
    """Guess if file is tv or movie based on parsed info."""
    if parsed["season"] is not None or parsed["episode"] is not None:
        return "tv"
    parent = parsed["context"]["parent_folder"].lower()
    grandparent = parsed["context"]["grandparent_folder"].lower()
    if "movie" in parent or "film" in parent:
        return "movie"
    if "movie" in grandparent or "film" in grandparent:
        return "movie"
    if "tv" in parent or "show" in parent or "series" in parent:
        return "tv"
    return "tv"  # default to tv


def llm_resolve(parsed: dict, candidates: list, llm) -> dict | None:
    """Use LLM to resolve ambiguous or uncertain matches."""
    candidate_text = "\n".join([
        f"- {c['title']} ({c['year']}) — popularity: {c['popularity']}"
        for c in candidates
    ])

    context = f"""
Filename: {parsed['filename']}
Parent folder: {parsed['context']['parent_folder']}
Grandparent folder: {parsed['context']['grandparent_folder']}
Extracted title: {parsed['cleaned_title']}
Season: {parsed['season']}
Episode: {parsed['episode']}
Year: {parsed['year']}
"""

    prompt = f"""You are helping identify a media file for a Plex server.

Here is what we know about the file:
{context}

Here are the top TMDB candidates:
{candidate_text}

Which candidate is the most likely match? Reply with ONLY the title and year 
in this exact format: TITLE (YEAR)
If you genuinely cannot determine the match, reply with: UNKNOWN
"""

    response = llm.invoke([
        SystemMessage(content="You are a media identification assistant."),
        HumanMessage(content=prompt)
    ])

    answer = response.content.strip()
    print(f"  [LLM] {answer}")

    if answer == "UNKNOWN":
        return None

    for c in candidates:
        if c["title"].lower() in answer.lower():
            return c

    return None


def build_new_path(match: dict, parsed: dict, media_type: str) -> str | None:
    """Build the TRaSH-standard path for a matched file."""
    extension = "." + parsed["filename"].split(".")[-1]
    title = match["title"]
    year = match["year"] or parsed["year"] or "Unknown"

    if media_type == "tv":
        season = parsed["season"]
        episode = parsed["episode"]

        if not season or not episode:
            return None

        episode_details = get_episode_details(match["id"], season, episode)
        episode_title = episode_details.get("title", "Unknown Episode")

        base = MEDIA_PATH + "/TV Shows"
        return build_tv_path(base, title, year, season, episode, episode_title, extension)

    else:
        base = MEDIA_PATH + "/Movies"
        return build_movie_path(base, title, year, extension)


def run_agent():
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.3-70b-versatile"
    )

    print("[Agent] Scanning for badly named files...")
    files = scan_badly_named()
    print(f"[Agent] Found {len(files)} badly named files\n")

    stats = {"auto_renamed": 0, "llm_resolved": 0, "flagged": 0, "skipped": 0}

    for item in files:
        path = item["path"]
        filename = item["filename"]
        print(f"[Agent] Processing: {filename}")

        # Parse
        parsed = parse_filename(path)
        media_type = detect_media_type(parsed)
        print(f"  Type: {media_type} | Title: {parsed['cleaned_title']} | S{parsed['season']}E{parsed['episode']}")

        # Confidence check
        result = get_best_match(parsed, media_type)

        if result["unidentifiable"]:
            print(f"  Unidentifiable — flagging for review")
            log_decision(filename, "flagged", "Could not extract title", False)
            stats["flagged"] += 1
            continue

        # High confidence, no ambiguity → rename automatically
        if result["score"] >= CONFIDENCE_THRESHOLD and not result["ambiguous"]:
            print(f"  High confidence ({result['score']}) — auto renaming")
            new_path = build_new_path(result["match"], parsed, media_type)
            if not new_path:
                print(f"  Could not build path — skipping")
                stats["skipped"] += 1
                continue
            rename_result = rename_file(path, new_path, dry_run=DRY_RUN)
            log_decision(filename, "auto_rename", f"Confidence: {result['score']}", rename_result["success"], {
                "new_path": new_path,
                "dry_run": DRY_RUN,
                "match": result["match"]["title"]
            })
            print(f"  → {new_path}")
            stats["auto_renamed"] += 1

        # Low confidence or ambiguous → try LLM
        else:
            print(f"  Low confidence ({result['score']}) or ambiguous — asking LLM")
            match = llm_resolve(parsed, result["candidates"], llm)

            if not match:
                print(f"  LLM could not resolve — flagging for review")
                log_decision(filename, "flagged", "LLM could not resolve", False)
                stats["flagged"] += 1
                continue

            new_path = build_new_path(match, parsed, media_type)
            if not new_path:
                print(f"  Could not build path — skipping")
                stats["skipped"] += 1
                continue

            rename_result = rename_file(path, new_path, dry_run=DRY_RUN)
            log_decision(filename, "llm_rename", f"LLM resolved to {match['title']}", rename_result["success"], {
                "new_path": new_path,
                "dry_run": DRY_RUN,
                "match": match["title"]
            })
            print(f"  → {new_path}")
            stats["llm_resolved"] += 1

    print(f"\n[Agent] Done.")
    print(f"  Auto renamed: {stats['auto_renamed']}")
    print(f"  LLM resolved: {stats['llm_resolved']}")
    print(f"  Flagged for review: {stats['flagged']}")
    print(f"  Skipped: {stats['skipped']}")


if __name__ == "__main__":
    run_agent()