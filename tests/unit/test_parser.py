from agent.core import detect_media_type
from agent.tools.parser import parse_filename

TV = "/mnt/media/TV Shows"
MOVIES = "/mnt/media/Movies"


def parse(path):
    return parse_filename(path)


def mtype(path):
    return detect_media_type(parse_filename(path))


# ---------------------------------------------------------------------------
# Standard SxEx format
# ---------------------------------------------------------------------------


def test_standard_sxe():
    p = parse(f"{TV}/Breaking Bad/Season 1/Breaking.Bad.S01E03.720p.BluRay.mkv")
    assert p["cleaned_title"] == "Breaking Bad"
    assert p["season"] == 1
    assert p["episode"] == 3


def test_episode_only_filename():
    p = parse(f"{TV}/The Office/Season 2/S02E03.mkv")
    assert p["cleaned_title"] == "The Office"
    assert p["season"] == 2
    assert p["episode"] == 3


def test_nxn_format():
    p = parse(f"{TV}/The Simpsons/Season 10/The Simpsons [10x12] Sunday Cruddy Sunday.avi")
    assert p["cleaned_title"] == "The Simpsons"
    assert p["season"] == 10
    assert p["episode"] == 12


# ---------------------------------------------------------------------------
# Season 0 / specials
# ---------------------------------------------------------------------------


def test_season_zero_not_falsy():
    p = parse(f"{TV}/Steven Universe/Season 0/Steven Universe S00E01 Pilot.mp4")
    assert p["season"] == 0
    assert p["episode"] == 1


# ---------------------------------------------------------------------------
# Movie special format (SxxMxx)
# ---------------------------------------------------------------------------


def test_movie_special_format():
    path = f"{TV}/Steven Universe/Season 5/Steven Universe S05M01 The Movie.m4v"
    p = parse(path)
    assert p["cleaned_title"] == "Steven Universe The Movie"
    assert p["season"] is None
    assert p["episode"] is None
    assert mtype(path) == "movie"


# ---------------------------------------------------------------------------
# Leading bracket stripping
# ---------------------------------------------------------------------------


def test_leading_bracket_pseudo():
    filename = "[pseudo] Rick and Morty S01E02 Lawnmower Dog [BDRip] [1080p] [h.265].mkv"
    p = parse(f"{TV}/Rick and Morty/Season 1/{filename}")
    assert p["cleaned_title"] == "Rick and Morty"
    assert p["season"] == 1
    assert p["episode"] == 2


def test_leading_bracket_wrapping_whole_filename():
    folder = "Rick and Morty - Season 3 (2017) [1080p]"
    filename = "[Rick.and.Morty.S03E10.The.Rickchurian.Mortydate.1080p.Amazon].WEB-DL.x264-Rapta.mkv"
    p = parse(f"{TV}/Rick and Morty/{folder}/{filename}")
    assert p["cleaned_title"] == "Rick and Morty"
    assert p["season"] == 3
    assert p["episode"] == 10


def test_leading_bracket_s03e01():
    folder = "Rick and Morty - Season 3 (2017) [1080p]"
    filename = "[Rick.and.Morty.S03E01.The.Rickshank.Rickdemption.1080p.Amazon].WEB-DL.x264-Rapta.mkv"
    p = parse(f"{TV}/Rick and Morty/{folder}/{filename}")
    assert p["cleaned_title"] == "Rick and Morty"
    assert p["season"] == 3
    assert p["episode"] == 1


# ---------------------------------------------------------------------------
# Underscore episode codes (_507_)
# ---------------------------------------------------------------------------


def test_underscore_episode_507():
    p = parse(f"{TV}/Hey Arnold!/Season.5/Hey.Arnold!_507__Married--.avi")
    assert p["cleaned_title"] == "Hey Arnold!"
    assert p["season"] == 5
    assert p["episode"] == 7


def test_underscore_episode_207():
    p = parse(f"{TV}/Hey Arnold!/Season.2/Hey.Arnold!_207__Arnold's.Halloween--[RUS].avi")
    assert p["cleaned_title"] == "Hey Arnold!"
    assert p["season"] == 2
    assert p["episode"] == 7


def test_underscore_episode_303():
    filename = "Hey.Arnold!_303__Casa.Paradiso__Gerald's.Tonsils--[RUS].avi"
    p = parse(f"{TV}/Hey Arnold!/Season.3/{filename}")
    assert p["cleaned_title"] == "Hey Arnold!"
    assert p["season"] == 3
    assert p["episode"] == 3


def test_standard_hey_arnold():
    p = parse(f"{TV}/Hey Arnold/Season 5/Hey.Arnold.S05E07.avi")
    assert p["cleaned_title"] == "Hey Arnold"
    assert p["season"] == 5
    assert p["episode"] == 7


# ---------------------------------------------------------------------------
# Folder-based season extraction
# ---------------------------------------------------------------------------


def test_version_folder_as_season():
    filename = "The IT Crowd S05 The Internet Is Coming DVDRip BONE.mp4"
    p = parse(f"{TV}/The IT Crowd/Version 5.0/{filename}")
    assert p["cleaned_title"] == "The IT Crowd"
    assert p["season"] == 5
    assert p["episode"] is None


def test_himym_season_in_folder():
    folder = "How I Met Your Mother Season 6"
    filename = "How I Met Your Mother S06E16 Desperation Day (1080p x265 Joy).mkv"
    p = parse(f"{TV}/How I Met Your Mother/{folder}/{filename}")
    assert p["cleaned_title"] == "How I Met Your Mother"
    assert p["season"] == 6
    assert p["episode"] == 16


def test_leading_digit_folder():
    p = parse(f"{TV}/The Simpsons/5The Simpsons - Season Five/Homer Goes To College.mp4")
    assert p["cleaned_title"] == "The Simpsons"
    assert p["season"] == 5


def test_leading_digit_folder_rosebud():
    p = parse(f"{TV}/The Simpsons/5The Simpsons - Season Five/Rosebud.mp4")
    assert p["cleaned_title"] == "The Simpsons"
    assert p["season"] == 5


def test_leading_digit_folder_treehouse():
    p = parse(f"{TV}/The Simpsons/5The Simpsons - Season Five/Treehouse of Horror IV.mp4")
    assert p["cleaned_title"] == "The Simpsons"
    assert p["season"] == 5


# ---------------------------------------------------------------------------
# Simpsons title-only files (no episode number)
# ---------------------------------------------------------------------------


def test_simpsons_no_episode_number():
    p = parse(f"{TV}/The Simpsons/Season 9/Lisa's Sax.m4v")
    assert p["cleaned_title"] == "The Simpsons"
    assert p["season"] == 9
    assert p["episode"] is None


def test_simpsons_show_name_prefix_stripped():
    p = parse(f"{TV}/The Simpsons/Season 9/The Simpsons - Lisa's Sax.m4v")
    assert p["cleaned_title"] == "The Simpsons"
    assert p["season"] == 9
    assert p["episode"] is None


# ---------------------------------------------------------------------------
# Movies
# ---------------------------------------------------------------------------


def test_movie_with_year_in_folder():
    path = f"{MOVIES}/Whiplash (2014)/Whiplash.2014.1080p.BluRay.x264.YIFY.mp4"
    p = parse(path)
    assert p["cleaned_title"] == "Whiplash"
    assert p["season"] is None
    assert p["episode"] is None
    assert mtype(path) == "movie"


def test_movie_love_actually():
    path = f"{MOVIES}/Love Actually (2003)/Love.Actually.2003.1080p.BluRay.x264.YIFY.mp4"
    assert parse(path)["cleaned_title"] == "Love Actually"
    assert mtype(path) == "movie"


def test_movie_grand_budapest():
    path = f"{MOVIES}/The Grand Budapest Hotel (2014)/The.Grand.Budapest.Hotel.2014.1080p.BRRip.x264.mp4"
    assert parse(path)["cleaned_title"] == "The Grand Budapest Hotel"
    assert mtype(path) == "movie"


def test_movie_after_yang():
    path = f"{MOVIES}/After Yang/After.Yang.2021.2160p.4K.WEB.x265.10bit.AAC5.1-[YTS.MX].mkv"
    assert parse(path)["cleaned_title"] == "After Yang"
    assert mtype(path) == "movie"


def test_movie_oceans_eleven():
    p = parse(f"{MOVIES}/Oceans Eleven (2001)/Oceans.Eleven.2001.1080p.BluRay.H264.AAC-RARBG.mp4")
    assert p["cleaned_title"] == "Oceans Eleven"


def test_movie_intouchables_french_tag():
    subfolder = "The.Intouchables.2011.FRENCH.1080p.BluRay.H264.AAC-VXT"
    filename = "The.Intouchables.2011.FRENCH.1080p.BluRay.H264.AAC-VXT.mp4"
    p = parse(f"{MOVIES}/The Intouchables (2011)/{subfolder}/{filename}")
    assert p["cleaned_title"] == "The Intouchables"


def test_movie_your_name_bracket_and_dubbed():
    p = parse(f"{MOVIES}/Your Name (dubbed) (2016)/[Your.Name].2016.mp4")
    assert p["cleaned_title"] == "Your Name"


def test_movie_hotarubi():
    filename = "[Aenianos] Hotarubi no Mori e (BD 1080p hi10p FLAC) [rich_jc].mkv"
    p = parse(f"{MOVIES}/To the Forest of Firefly Lights (2011)/{filename}")
    assert p["cleaned_title"] == "To the Forest of Firefly Lights"


def test_movie_a_silent_voice():
    p = parse(f"{MOVIES}/A Silent Voice (2016)/A.Silent.Voice.2016.1080p.BluRay.x264-[YTS.AM].mp4")
    assert p["cleaned_title"] == "A Silent Voice"


# ---------------------------------------------------------------------------
# 30 for 30 — make sure "30" isn't parsed as season 30
# ---------------------------------------------------------------------------


def test_30_for_30_birth_of_big_air():
    p = parse(f"{MOVIES}/30 for 30/The Birth of Big Air (2009)/The Birth of Big Air (2009).avi")
    assert p["cleaned_title"] == "The Birth of Big Air"
    assert p["season"] is None


def test_30_for_30_winning_time():
    folder = "Winning Time Reggie Miller vs The New York Knicks (2010)"
    p = parse(f"{MOVIES}/30 for 30/{folder}/{folder}.avi")
    assert p["cleaned_title"] == "Winning Time Reggie Miller vs The New York Knicks"
    assert p["season"] is None


# ---------------------------------------------------------------------------
# Media type detection
# ---------------------------------------------------------------------------


def test_detect_tv_from_path():
    assert mtype(f"{TV}/Severance/Season 1/Severance.S01E04.720p.ATVP.WEBRip.x264-GalaxyTV.mkv") == "tv"


def test_detect_movie_from_path():
    assert mtype(f"{MOVIES}/Whiplash (2014)/Whiplash.2014.1080p.BluRay.x264.YIFY.mp4") == "movie"
