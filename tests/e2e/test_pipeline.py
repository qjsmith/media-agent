"""
E2E pipeline inspection — not a pass/fail test suite.
Run locally to inspect which files would go to the LLM.

    pytest tests/e2e/ -s

Or run directly:

    python tests/e2e/test_pipeline.py
"""
from agent.tools.parser import parse_filename
from agent.core import detect_media_type, build_new_path
from agent.tools.confidence import get_best_match

CASES = [
    "/mnt/media/TV Shows/Breaking Bad/Season 1/Breaking.Bad.S01E03.720p.BluRay.mkv",
    "/mnt/media/TV Shows/The Office/Season 2/S02E03.mkv",
    "/mnt/media/TV Shows/Rick and Morty/Rick and Morty - Season 3 (2017) [1080p]/[Rick.and.Morty.S03E10.The.Rickchurian.Mortydate.1080p.Amazon].WEB-DL.x264-Rapta.mkv",
    "/mnt/media/Movies/Whiplash (2014)/Whiplash.2014.1080p.BluRay.x264.YIFY.mp4",
    "/mnt/media/Movies/After Yang/After.Yang.2021.2160p.4K.WEB.x265.10bit.AAC5.1-[YTS.MX].mkv",
    "/mnt/media/Movies/Your Name (dubbed) (2016)/[Your.Name].2016.mp4",
    "/mnt/media/Movies/To the Forest of Firefly Lights (2011)/[Aenianos] Hotarubi no Mori e (BD 1080p hi10p FLAC) [rich_jc].mkv",
]


def test_pipeline_inspection():
    """Prints confidence scores for all cases. Not a pass/fail test."""
    print("\n--- Pipeline inspection ---\n")
    for path in CASES:
        parsed = parse_filename(path)
        media_type = detect_media_type(parsed)
        result = get_best_match(parsed, media_type)
        action = (
            "AUTO RENAME"
            if result["score"] >= 90 and not result["ambiguous"]
            else "LLM/FLAG"
        )
        match_title = result["match"]["title"] if result["match"] else "NO MATCH"
        print(f"[{action}] {path.split('/')[-1]}")
        print(f"  title={parsed['cleaned_title']} score={result['score']} match={match_title}")
        print()


if __name__ == "__main__":
    test_pipeline_inspection()
