import pytest
from agent.tools.parser import parse_filename
from agent.core import detect_media_type


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse(path):
    return parse_filename(path)


def media_type(path):
    return detect_media_type(parse_filename(path))


# ---------------------------------------------------------------------------
# Standard SxEx format
# ---------------------------------------------------------------------------

def test_standard_sxe():
    p = parse("/mnt/media/TV Shows/Breaking Bad/Season 1/Breaking.Bad.S01E03.720p.BluRay.mkv")
    assert p["cleaned_title"] == "Breaking Bad"
    assert p["season"] == 1
    assert p["episode"] == 3

def test_episode_only_filename():
    p = parse("/mnt/media/TV Shows/The Office/Season 2/S02E03.mkv")
    assert p["cleaned_title"] == "The Office"
    assert p["season"] == 2
    assert p["episode"] == 3

def test_nxn_format():
    p = parse("/mnt/media/TV Shows/The Simpsons/Season 10/The Simpsons [10x12] Sunday Cruddy Sunday.avi")
    assert p["cleaned_title"] == "The Simpsons"
    assert p["season"] == 10
    assert p["episode"] == 12


# ---------------------------------------------------------------------------
# Season 0 / specials
# ---------------------------------------------------------------------------

def test_season_zero_not_falsy():
    p = parse("/mnt/media/TV Shows/Steven Universe/Season 0/Steven Universe S00E01 Pilot.mp4")
    assert p["season"] == 0
    assert p["episode"] == 1


# ---------------------------------------------------------------------------
# Movie special format (SxxMxx)
# ---------------------------------------------------------------------------

def test_movie_special_format():
    p = parse("/mnt/media/TV Shows/Steven Universe/Season 5/Steven Universe S05M01 The Movie.m4v")
    assert p["cleaned_title"] == "Steven Universe The Movie"
    assert p["season"] is None
    assert p["episode"] is None
    assert media_type("/mnt/media/TV Shows/Steven Universe/Season 5/Steven Universe S05M01 The Movie.m4v") == "movie"


# ---------------------------------------------------------------------------
# Leading bracket stripping
# ---------------------------------------------------------------------------

def test_leading_bracket_pseudo():
    p = parse("/mnt/media/TV Shows/Rick and Morty/Season 1/[pseudo] Rick and Morty S01E02 Lawnmower Dog [BDRip] [1080p] [h.265].mkv")
    assert p["cleaned_title"] == "Rick and Morty"
    assert p["season"] == 1
    assert p["episode"] == 2

def test_leading_bracket_wrapping_whole_filename():
    p = parse("/mnt/media/TV Shows/Rick and Morty/Rick and Morty - Season 3 (2017) [1080p]/[Rick.and.Morty.S03E10.The.Rickchurian.Mortydate.1080p.Amazon].WEB-DL.x264-Rapta.mkv")
    assert p["cleaned_title"] == "Rick and Morty"
    assert p["season"] == 3
    assert p["episode"] == 10

def test_leading_bracket_s03e01():
    p = parse("/mnt/media/TV Shows/Rick and Morty/Rick and Morty - Season 3 (2017) [1080p]/[Rick.and.Morty.S03E01.The.Rickshank.Rickdemption.1080p.Amazon].WEB-DL.x264-Rapta.mkv")
    assert p["cleaned_title"] == "Rick and Morty"
    assert p["season"] == 3
    assert p["episode"] == 1


# ---------------------------------------------------------------------------
# Underscore episode codes (_507_)
# ---------------------------------------------------------------------------

def test_underscore_episode_507():
    p = parse("/mnt/media/TV Shows/Hey Arnold!/Season.5/Hey.Arnold!_507__Married--.avi")
    assert p["cleaned_title"] == "Hey Arnold!"
    assert p["season"] == 5
    assert p["episode"] == 7

def test_underscore_episode_207():
    p = parse("/mnt/media/TV Shows/Hey Arnold!/Season.2/Hey.Arnold!_207__Arnold's.Halloween--[RUS].avi")
    assert p["cleaned_title"] == "Hey Arnold!"
    assert p["season"] == 2
    assert p["episode"] == 7

def test_underscore_episode_303():
    p = parse("/mnt/media/TV Shows/Hey Arnold!/Season.3/Hey.Arnold!_303__Casa.Paradiso__Gerald's.Tonsils--[RUS].avi")
    assert p["cleaned_title"] == "Hey Arnold!"
    assert p["season"] == 3
    assert p["episode"] == 3

def test_standard_hey_arnold():
    p = parse("/mnt/media/TV Shows/Hey Arnold/Season 5/Hey.Arnold.S05E07.avi")
    assert p["cleaned_title"] == "Hey Arnold"
    assert p["season"] == 5
    assert p["episode"] == 7


# ---------------------------------------------------------------------------
# Folder-based season extraction
# ---------------------------------------------------------------------------

def test_version_folder_as_season():
    p = parse("/mnt/media/TV Shows/The IT Crowd/Version 5.0/The IT Crowd S05 The Internet Is Coming DVDRip BONE.mp4")
    assert p["cleaned_title"] == "The IT Crowd"
    assert p["season"] == 5
    assert p["episode"] is None

def test_himym_season_in_folder():
    p = parse("/mnt/media/TV Shows/How I Met Your Mother/How I Met Your Mother Season 6/How I Met Your Mother S06E16 Desperation Day (1080p x265 Joy).mkv")
    assert p["cleaned_title"] == "How I Met Your Mother"
    assert p["season"] == 6
    assert p["episode"] == 16

def test_leading_digit_folder():
    p = parse("/mnt/media/TV Shows/The Simpsons/5The Simpsons - Season Five/Homer Goes To College.mp4")
    assert p["cleaned_title"] == "The Simpsons"
    assert p["season"] == 5

def test_leading_digit_folder_rosebud():
    p = parse("/mnt/media/TV Shows/The Simpsons/5The Simpsons - Season Five/Rosebud.mp4")
    assert p["cleaned_title"] == "The Simpsons"
    assert p["season"] == 5

def test_leading_digit_folder_treehouse():
    p = parse("/mnt/media/TV Shows/The Simpsons/5The Simpsons - Season Five/Treehouse of Horror IV.mp4")
    assert p["cleaned_title"] == "The Simpsons"
    assert p["season"] == 5


# ---------------------------------------------------------------------------
# Simpsons title-only files (no episode number)
# ---------------------------------------------------------------------------

def test_simpsons_no_episode_number():
    p = parse("/mnt/media/TV Shows/The Simpsons/Season 9/Lisa's Sax.m4v")
    assert p["cleaned_title"] == "The Simpsons"
    assert p["season"] == 9
    assert p["episode"] is None

def test_simpsons_show_name_prefix_stripped():
    p = parse("/mnt/media/TV Shows/The Simpsons/Season 9/The Simpsons - Lisa's Sax.m4v")
    assert p["cleaned_title"] == "The Simpsons"
    assert p["season"] == 9
    assert p["episode"] is None


# ---------------------------------------------------------------------------
# Movies
# ---------------------------------------------------------------------------

def test_movie_with_year_in_folder():
    p = parse("/mnt/media/Movies/Whiplash (2014)/Whiplash.2014.1080p.BluRay.x264.YIFY.mp4")
    assert p["cleaned_title"] == "Whiplash"
    assert p["season"] is None
    assert p["episode"] is None
    assert media_type("/mnt/media/Movies/Whiplash (2014)/Whiplash.2014.1080p.BluRay.x264.YIFY.mp4") == "movie"

def test_movie_love_actually():
    p = parse("/mnt/media/Movies/Love Actually (2003)/Love.Actually.2003.1080p.BluRay.x264.YIFY.mp4")
    assert p["cleaned_title"] == "Love Actually"
    assert media_type("/mnt/media/Movies/Love Actually (2003)/Love.Actually.2003.1080p.BluRay.x264.YIFY.mp4") == "movie"

def test_movie_grand_budapest():
    p = parse("/mnt/media/Movies/The Grand Budapest Hotel (2014)/The.Grand.Budapest.Hotel.2014.1080p.BRRip.x264.mp4")
    assert p["cleaned_title"] == "The Grand Budapest Hotel"
    assert media_type("/mnt/media/Movies/The Grand Budapest Hotel (2014)/The.Grand.Budapest.Hotel.2014.1080p.BRRip.x264.mp4") == "movie"

def test_movie_after_yang():
    p = parse("/mnt/media/Movies/After Yang/After.Yang.2021.2160p.4K.WEB.x265.10bit.AAC5.1-[YTS.MX].mkv")
    assert p["cleaned_title"] == "After Yang"
    assert media_type("/mnt/media/Movies/After Yang/After.Yang.2021.2160p.4K.WEB.x265.10bit.AAC5.1-[YTS.MX].mkv") == "movie"

def test_movie_oceans_eleven():
    p = parse("/mnt/media/Movies/Oceans Eleven (2001)/Oceans.Eleven.2001.1080p.BluRay.H264.AAC-RARBG.mp4")
    assert p["cleaned_title"] == "Oceans Eleven"

def test_movie_intouchables_french_tag():
    p = parse("/mnt/media/Movies/The Intouchables (2011)/The.Intouchables.2011.FRENCH.1080p.BluRay.H264.AAC-VXT/The.Intouchables.2011.FRENCH.1080p.BluRay.H264.AAC-VXT.mp4")
    assert p["cleaned_title"] == "The Intouchables"

def test_movie_your_name_bracket_and_dubbed():
    p = parse("/mnt/media/Movies/Your Name (dubbed) (2016)/[Your.Name].2016.mp4")
    assert p["cleaned_title"] == "Your Name"

def test_movie_hotarubi():
    p = parse("/mnt/media/Movies/To the Forest of Firefly Lights (2011)/[Aenianos] Hotarubi no Mori e (BD 1080p hi10p FLAC) [rich_jc].mkv")
    assert p["cleaned_title"] == "To the Forest of Firefly Lights"

def test_movie_a_silent_voice():
    p = parse("/mnt/media/Movies/A Silent Voice (2016)/A.Silent.Voice.2016.1080p.BluRay.x264-[YTS.AM].mp4")
    assert p["cleaned_title"] == "A Silent Voice"


# ---------------------------------------------------------------------------
# 30 for 30 — make sure "30" isn't parsed as season 30
# ---------------------------------------------------------------------------

def test_30_for_30_birth_of_big_air():
    p = parse("/mnt/media/Movies/30 for 30/The Birth of Big Air (2009)/The Birth of Big Air (2009).avi")
    assert p["cleaned_title"] == "The Birth of Big Air"
    assert p["season"] is None

def test_30_for_30_winning_time():
    p = parse("/mnt/media/Movies/30 for 30/Winning Time Reggie Miller vs The New York Knicks (2010)/Winning Time Reggie Miller vs The New York Knicks (2010).avi")
    assert p["cleaned_title"] == "Winning Time Reggie Miller vs The New York Knicks"
    assert p["season"] is None


# ---------------------------------------------------------------------------
# Media type detection
# ---------------------------------------------------------------------------

def test_detect_tv_from_path():
    assert media_type("/mnt/media/TV Shows/Severance/Season 1/Severance.S01E04.720p.ATVP.WEBRip.x264-GalaxyTV.mkv") == "tv"

def test_detect_movie_from_path():
    assert media_type("/mnt/media/Movies/Whiplash (2014)/Whiplash.2014.1080p.BluRay.x264.YIFY.mp4") == "movie"
