from agent.tools.parser import parse_filename
from agent.core import detect_media_type, build_new_path
from agent.tools.confidence import get_best_match

test_cases = [
    # (path, expected_title, expected_season, expected_episode, expected_media_type)
    ('/mnt/media/TV Shows/Breaking Bad/Season 1/Breaking.Bad.S01E03.720p.BluRay.mkv', 'Breaking Bad', 1, 3, 'tv'),
    ('/mnt/media/TV Shows/The Office/Season 2/S02E03.mkv', 'The Office', 2, 3, 'tv'),
    ('/mnt/media/TV Shows/The Simpsons/Season 9/Lisa\'s Sax.m4v', 'The Simpsons', 9, None, 'tv'),
    ('/mnt/media/TV Shows/The Simpsons/Season 9/The Simpsons - Lisa\'s Sax.m4v', 'The Simpsons', 9, None, 'tv'),
    ('/mnt/media/TV Shows/Steven Universe/Season 5/Steven Universe S05M01 The Movie.m4v', 'Steven Universe The Movie', None, None, 'movie'),
    ('/mnt/media/TV Shows/Steven Universe/Season 0/Steven Universe S00E01 Pilot.mp4', 'Steven Universe', 0, 1, 'tv'),
    ('/mnt/media/TV Shows/Rick and Morty/Season 3/[Rick.and.Morty.S03E03.Pickle.Rick.1080p.Amazon].WEB-DL.x264-Rapta.mkv', 'Rick and Morty', 3, 3, 'tv'),
    ('/mnt/media/Movies/Whiplash (2014)/Whiplash.2014.1080p.BluRay.x264.YIFY.mp4', 'Whiplash', None, None, 'movie'),
    ('/mnt/media/Movies/Love Actually (2003)/Love.Actually.2003.1080p.BluRay.x264.YIFY.mp4', 'Love Actually', None, None, 'movie'),
    # Regression — make sure bracket strip doesn't break normal titles
    ('/mnt/media/TV Shows/The Simpsons/Season 10/The Simpsons [10x12] Sunday Cruddy Sunday.avi', 'The Simpsons', 10, 12, 'tv'),
    ('/mnt/media/Movies/The Grand Budapest Hotel (2014)/The.Grand.Budapest.Hotel.2014.1080p.BRRip.x264.mp4', 'The Grand Budapest Hotel', None, None, 'movie'),
    ('/mnt/media/TV Shows/Hey Arnold/Season 5/Hey.Arnold.S05E07.avi', 'Hey Arnold', 5, 7, 'tv'),
    ('/mnt/media/TV Shows/Rick and Morty/Season 1/[pseudo] Rick and Morty S01E02 Lawnmower Dog [BDRip] [1080p] [h.265].mkv', 'Rick and Morty', 1, 2, 'tv'),
    ('/mnt/media/TV Shows/Severance/Season 1/Severance.S01E04.720p.ATVP.WEBRip.x264-GalaxyTV.mkv', 'Severance', 1, 4, 'tv'),
    # --- Flagged cases that should be fixed ---
    # Rick and Morty Amazon format — leading bracket wrapping whole filename
    ('/mnt/media/TV Shows/Rick and Morty/Rick and Morty - Season 3 (2017) [1080p]/[Rick.and.Morty.S03E10.The.Rickchurian.Mortydate.1080p.Amazon].WEB-DL.x264-Rapta.mkv', 'Rick and Morty', 3, 10, 'tv'),
    ('/mnt/media/TV Shows/Rick and Morty/Rick and Morty - Season 3 (2017) [1080p]/[Rick.and.Morty.S03E01.The.Rickshank.Rickdemption.1080p.Amazon].WEB-DL.x264-Rapta.mkv', 'Rick and Morty', 3, 1, 'tv'),

    # Hey Arnold _507_ episode code format
    ('/mnt/media/TV Shows/Hey Arnold!/Season.5/Hey.Arnold!_507__Married--.avi', 'Hey Arnold!', 5, 7, 'tv'),
    ('/mnt/media/TV Shows/Hey Arnold!/Season.2/Hey.Arnold!_207__Arnold\'s.Halloween--[RUS].avi', 'Hey Arnold!', 2, 7, 'tv'),
    ('/mnt/media/TV Shows/Hey Arnold!/Season.3/Hey.Arnold!_303__Casa.Paradiso__Gerald\'s.Tonsils--[RUS].avi', 'Hey Arnold!', 3, 3, 'tv'),

    # IT Crowd Version 5.0 folder — should parse as Season 5
    ('/mnt/media/TV Shows/The IT Crowd/Version 5.0/The IT Crowd S05 The Internet Is Coming DVDRip BONE.mp4', 'The IT Crowd', 5, None, 'tv'),

    # HIMYM — season in folder name
    ('/mnt/media/TV Shows/How I Met Your Mother/How I Met Your Mother Season 6/How I Met Your Mother S06E16 Desperation Day (1080p x265 Joy).mkv', 'How I Met Your Mother', 6, 16, 'tv'),

    # Movies — already in correctly named folders
    ('/mnt/media/Movies/After Yang/After.Yang.2021.2160p.4K.WEB.x265.10bit.AAC5.1-[YTS.MX].mkv', 'After Yang', None, None, 'movie'),
    ('/mnt/media/Movies/Oceans Eleven (2001)/Oceans.Eleven.2001.1080p.BluRay.H264.AAC-RARBG.mp4', 'Oceans Eleven', None, None, 'movie'),
    ('/mnt/media/Movies/The Intouchables (2011)/The.Intouchables.2011.FRENCH.1080p.BluRay.H264.AAC-VXT/The.Intouchables.2011.FRENCH.1080p.BluRay.H264.AAC-VXT.mp4', 'The Intouchables', None, None, 'movie'),
    ('/mnt/media/Movies/Your Name (dubbed) (2016)/[Your.Name].2016.mp4', 'Your Name', None, None, 'movie'),
    ('/mnt/media/Movies/To the Forest of Firefly Lights (2011)/[Aenianos] Hotarubi no Mori e (BD 1080p hi10p FLAC) [rich_jc].mkv', 'To the Forest of Firefly Lights', None, None, 'movie'),
    ('/mnt/media/Movies/A Silent Voice (2016)/A.Silent.Voice.2016.1080p.BluRay.x264-[YTS.AM].mp4', 'A Silent Voice', None, None, 'movie'),

    # --- Cases that should stay flagged/skipped (correctly handled) ---
    # Springfield.mp4 — genuinely unidentifiable, expect None title or Simpsons
    # Hey Arnold Bonus — no TMDB match, correctly flagged
    # Steven Universe Xtras — no season, correctly flagged
]

passed = 0
failed = 0

for path, exp_title, exp_season, exp_episode, exp_type in test_cases:
    parsed = parse_filename(path)
    media_type = detect_media_type(parsed)

    ok = (
        parsed['cleaned_title'] == exp_title and
        parsed['season'] == exp_season and
        parsed['episode'] == exp_episode and
        media_type == exp_type
    )

    if ok:
        passed += 1
        print(f'✓ PASS: {path.split("/")[-1]}')
    else:
        failed += 1
        print(f'✗ FAIL: {path.split("/")[-1]}')
        print(f'       title:   got={parsed["cleaned_title"]} expected={exp_title}')
        print(f'       season:  got={parsed["season"]} expected={exp_season}')
        print(f'       episode: got={parsed["episode"]} expected={exp_episode}')
        print(f'       type:    got={media_type} expected={exp_type}')

print(f'\n{passed}/{passed+failed} tests passed')

print(f'\n--- Pipeline failures ---')
for path, exp_title, exp_season, exp_episode, exp_type in test_cases:
    parsed = parse_filename(path)
    media_type = detect_media_type(parsed)
    result = get_best_match(parsed, media_type)
    new_path = build_new_path(result['match'], parsed, media_type) if result['match'] else None
    action = "AUTO RENAME" if result["score"] >= 90 and not result["ambiguous"] else "LLM/FLAG"
    if action == "LLM/FLAG":
        print(f'\nFile: {path.split("/")[-1]}')
        print(f'  title:    {parsed["cleaned_title"]}')
        print(f'  score:    {result["score"]}')
        print(f'  match:    {result["match"]["title"] if result["match"] else "NO MATCH"}')
        print(f'  new_path: {new_path}')