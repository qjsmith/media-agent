from langchain_groq import ChatGroq

from agent.tools.confidence import get_best_match
from agent.tools.llm import llm_resolve
from agent.tools.logger import log_decision
from agent.tools.media_type import detect_media_type
from agent.tools.metadata import get_episode_details, search_episode_by_title
from agent.tools.parser import parse_filename
from agent.tools.plex_refresh import refresh_plex_library
from agent.tools.renamer import build_movie_path, build_tv_path, rename_file
from agent.tools.scanner import scan_badly_named
from config import GROQ_API_KEY, MEDIA_PATH, PLEX_TOKEN, PLEX_URL

CONFIDENCE_THRESHOLD = 90.0
DRY_RUN = False
LLM_CALL_LIMIT = 25

TV_PATH = MEDIA_PATH + "/TV Shows"
MOVIE_PATH = MEDIA_PATH + "/Movies"


def build_new_path(match: dict, parsed: dict, media_type: str) -> str | None:
    """Build the TRaSH-standard path for a matched file."""
    extension = "." + parsed["filename"].split(".")[-1]
    title = match["title"]
    year = match["year"] or parsed["year"] or "Unknown"

    if media_type == "tv":
        season = parsed["season"]
        episode = parsed["episode"]

        if season is None:
            return None

        if not episode and parsed.get("episode_title"):
            print(f"  No episode number — searching by title: {parsed['episode_title']}")
            ep_result = search_episode_by_title(match["id"], season, parsed["episode_title"])
            if ep_result:
                episode = ep_result["episode_number"]
                episode_details = {"title": ep_result["title"]}
                print(f"  Found episode {episode}: {ep_result['title']}")
            else:
                print("  Could not match episode title — skipping")
                return None
        elif not episode:
            return None
        else:
            episode_details = get_episode_details(match["id"], season, episode)

        episode_title = episode_details.get("title", "Unknown Episode")
        return build_tv_path(TV_PATH, title, year, season, episode, episode_title, extension)

    else:
        return build_movie_path(MOVIE_PATH, title, year, extension)


def run_agent():
    llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.3-70b-versatile")

    print("[Agent] Scanning for badly named files...")
    files = scan_badly_named()
    print(f"[Agent] Found {len(files)} badly named files\n")

    stats = {"auto_renamed": 0, "llm_resolved": 0, "flagged": 0, "skipped": 0}
    llm_calls = 0

    for item in files:
        path = item["path"]
        filename = item["filename"]
        print(f"[Agent] Processing: {filename}")

        parsed = parse_filename(path)
        media_type = detect_media_type(parsed)
        print(f"  Type: {media_type} | Title: {parsed['cleaned_title']} | S{parsed['season']}E{parsed['episode']}")

        result = get_best_match(parsed, media_type)

        if result["unidentifiable"]:
            print("  Unidentifiable — flagging for review")
            log_decision(filename, "flagged", "Could not extract title", False)
            stats["flagged"] += 1
            continue

        if result["score"] >= CONFIDENCE_THRESHOLD and not result["ambiguous"]:
            print(f"  High confidence ({result['score']}) — auto renaming")
            new_path = build_new_path(result["match"], parsed, media_type)
            if not new_path:
                print("  Could not build path — skipping")
                log_decision(
                    filename,
                    "skipped",
                    "Could not build path",
                    False,
                    {
                        "parsed_season": parsed["season"],
                        "parsed_episode": parsed["episode"],
                        "cleaned_title": parsed["cleaned_title"],
                    },
                )
                stats["skipped"] += 1
                continue
            rename_result = rename_file(path, new_path, dry_run=DRY_RUN)
            log_decision(
                filename,
                "auto_rename",
                f"Confidence: {result['score']}",
                rename_result["success"],
                {
                    "new_path": new_path,
                    "dry_run": DRY_RUN,
                    "match": result["match"]["title"],
                },
            )
            print(f"  → {new_path}")
            stats["auto_renamed"] += 1

        else:
            print(f"  Low confidence ({result['score']}) or ambiguous — asking LLM")
            if llm_calls >= LLM_CALL_LIMIT:
                print("  LLM call limit reached — flagging for review")
                log_decision(filename, "flagged", "LLM call limit reached", False)
                stats["flagged"] += 1
                continue
            llm_calls += 1
            match = llm_resolve(parsed, result["candidates"], llm)

            if not match:
                print("  LLM could not resolve — flagging for review")
                log_decision(filename, "flagged", "LLM could not resolve", False)
                stats["flagged"] += 1
                continue

            new_path = build_new_path(match, parsed, media_type)
            if not new_path:
                print("  Could not build path — skipping")
                log_decision(
                    filename,
                    "skipped",
                    "Could not build path",
                    False,
                    {
                        "parsed_season": parsed["season"],
                        "parsed_episode": parsed["episode"],
                        "cleaned_title": parsed["cleaned_title"],
                    },
                )
                stats["skipped"] += 1
                continue

            rename_result = rename_file(path, new_path, dry_run=DRY_RUN)
            log_decision(
                filename,
                "llm_rename",
                f"LLM resolved to {match['title']}",
                rename_result["success"],
                {"new_path": new_path, "dry_run": DRY_RUN, "match": match["title"]},
            )
            print(f"  → {new_path}")
            stats["llm_resolved"] += 1

    print("\n[Agent] Done.")
    print(f"  Auto renamed:       {stats['auto_renamed']}")
    print(f"  LLM resolved:       {stats['llm_resolved']}")
    print(f"  Flagged for review: {stats['flagged']}")
    print(f"  Skipped:            {stats['skipped']}")
    print(f"  LLM calls made:     {llm_calls} / {LLM_CALL_LIMIT}")

    if not DRY_RUN:
        refresh_plex_library(PLEX_URL, PLEX_TOKEN)


if __name__ == "__main__":
    run_agent()
