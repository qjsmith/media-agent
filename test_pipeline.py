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
    ('/mnt/media/TV Shows/Rick and Morty/Season 3/[Rick.and.Morty.S03E03.Pickle.Rick.1080p.Amazon].WEB-DL.x264-Rapta.mkv', '[Rick and Morty', 3, 3, 'tv'),
    ('/mnt/media/Movies/Whiplash (2014)/Whiplash.2014.1080p.BluRay.x264.YIFY.mp4', 'Whiplash', None, None, 'movie'),
    ('/mnt/media/Movies/Love Actually (2003)/Love.Actually.2003.1080p.BluRay.x264.YIFY.mp4', 'Love Actually', None, None, 'movie'),
    # Regression — make sure bracket strip doesn't break normal titles
    ('/mnt/media/TV Shows/The Simpsons/Season 10/The Simpsons [10x12] Sunday Cruddy Sunday.avi', 'The Simpsons', 10, 12, 'tv'),
    ('/mnt/media/Movies/The Grand Budapest Hotel (2014)/The.Grand.Budapest.Hotel.2014.1080p.BRRip.x264.mp4', 'The Grand Budapest Hotel', None, None, 'movie'),
    ('/mnt/media/TV Shows/Hey Arnold/Season 5/Hey.Arnold.S05E07.avi', 'Hey Arnold', 5, 7, 'tv'),
    ('/mnt/media/TV Shows/Rick and Morty/Season 1/[pseudo] Rick and Morty S01E02 Lawnmower Dog [BDRip] [1080p] [h.265].mkv', 'Rick and Morty', 1, 2, 'tv'),
    ('/mnt/media/TV Shows/Severance/Season 1/Severance.S01E04.720p.ATVP.WEBRip.x264-GalaxyTV.mkv', 'Severance', 1, 4, 'tv'),
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

    status = '✓' if ok else '✗'
    if ok:
        passed += 1
    else:
        failed += 1
        print(f'{status} FAIL: {path.split("/")[-1]}')
        print(f'       title:   got={parsed["cleaned_title"]} expected={exp_title}')
        print(f'       season:  got={parsed["season"]} expected={exp_season}')
        print(f'       episode: got={parsed["episode"]} expected={exp_episode}')
        print(f'       type:    got={media_type} expected={exp_type}')
    if ok:
        print(f'{status} PASS: {path.split("/")[-1]}')

print(f'\n{passed}/{passed+failed} tests passed')

print(f'\n--- Full pipeline ---')
for path, exp_title, exp_season, exp_episode, exp_type in test_cases:
    parsed = parse_filename(path)
    media_type = detect_media_type(parsed)
    result = get_best_match(parsed, media_type)
    new_path = build_new_path(result['match'], parsed, media_type)
    print(f'\nFile: {path.split("/")[-1]}')
    print(f'  match:    {result["match"]["title"]} ({result["match"]["year"]})')
    print(f'  score:    {result["score"]}')
    print(f'  action:   {"AUTO RENAME" if result["score"] >= 90 and not result["ambiguous"] else "LLM/FLAG"}')
    print(f'  new_path: {new_path}')