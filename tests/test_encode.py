import os

import pytest
from mutagen.flac import FLAC

from conftest import DISCS
from encode import encode_track, clean_genre, suggest_genre, build_track_metadata
from rip_cd import generate_filenames


def disc_by_artist(artist):
    return next(disc for disc in DISCS if disc['artist'].strip() == artist)


# --- Genre cleaning ---

@pytest.mark.parametrize("raw,expected", [
    ("Data", ""),
    ("data", ""),
    ("Other", ""),
    ("Rock/Pop", "Rock/Pop"),
    ("pop rock", "Pop Rock"),
    ("New Age", "New Age"),
    ("  Rock  ", "Rock"),
])
def test_clean_genre(raw, expected):
    assert clean_genre(raw) == expected


# --- Genre suggestion ---

@pytest.mark.parametrize("raw,expected", [
    ("Rock", "Rock"),
    ("rock", "Rock"),
    ("Jazz", "Jazz"),
    ("JAZZ", "Jazz"),
    ("Electronic", "Electronic"),
    ("Techno", "Electronic"),
    ("techno", "Electronic"),
    ("Electronica", "Electronic"),
    ("Hip Hop", "Hip-Hop"),
    ("rap", "Hip-Hop"),
    ("R&B", "R&B / Soul"),
    ("soul", "R&B / Soul"),
    ("pop rock", "Rock"),
    ("indie rock", "Alternative"),
    ("hard rock", "Rock"),
    ("Rock/Pop", "Rock"),
    ("Data", None),
    ("data", None),
    ("Other", None),
    ("", None),
    ("  ", None),
    ("New Age", "New Age"),
    ("Classical", "Classical"),
    ("Bluegrass", "Bluegrass"),
])
def test_suggest_genre(raw, expected):
    assert suggest_genre(raw) == expected


# --- Metadata building ---

def test_genre_passed_through():
    disc = disc_by_artist("Duran Duran")
    metadata = build_track_metadata(disc, 0, "Rock")
    assert metadata["genre"] == "Rock"


def test_empty_genre_passed_through():
    disc = disc_by_artist("Duran Duran")
    metadata = build_track_metadata(disc, 0, "")
    assert metadata["genre"] == ""


def test_missing_year_is_empty():
    disc = disc_by_artist("Duran Duran")  # year is ""
    metadata = build_track_metadata(disc, 0, "Rock")
    assert metadata["date"] == ""


def test_compilation_has_track_artist():
    disc = disc_by_artist("Various Artists")  # Forrest Gump
    metadata = build_track_metadata(disc, 0, "Other")
    assert metadata["artist"] == "Jefferson Airplane"
    assert metadata["albumartist"] == "Various Artists"


def test_single_artist_metadata():
    disc = disc_by_artist("The Crystal Method")
    metadata = build_track_metadata(disc, 0, "Electronic")
    assert metadata["artist"] == "The Crystal Method"
    assert metadata["albumartist"] == "The Crystal Method"
    assert metadata["title"] == "Trip Like I Do"


# --- Encoding ---

def test_encode_single_track(sample_wav, tmp_path):
    metadata = {
        "title": "Test Track",
        "artist": "Test Artist",
        "album": "Test Album",
        "albumartist": "Test Artist",
        "date": "2024",
        "genre": "Rock",
        "tracknumber": "1",
        "totaltracks": "10"}
    flac_file = str(tmp_path / "Test Artist - 01 - Test Track.flac")
    encode_track(sample_wav, flac_file, metadata)
    assert os.path.exists(flac_file)
    audio = FLAC(flac_file)
    assert audio["title"] == ["Test Track"]
    assert audio["artist"] == ["Test Artist"]
    assert audio["genre"] == ["Rock"]


def test_empty_fields_not_tagged(sample_wav, tmp_path):
    """Empty year and genre should not appear as tags."""
    disc = disc_by_artist("Duran Duran")
    metadata = build_track_metadata(disc, 0, "")
    flac_file = str(tmp_path / "test.flac")
    encode_track(sample_wav, flac_file, metadata)
    audio = FLAC(flac_file)
    assert "date" not in audio, "Empty year should not be written as a tag"
    assert "genre" not in audio, "Empty genre should not be written as a tag"


def test_encode_full_album(sample_wav, tmp_path):
    """Encode an entire album using Track 1.wav for every track."""
    disc = disc_by_artist("The Crystal Method")
    folder, track_names = generate_filenames(disc)
    album_dir = tmp_path / folder
    album_dir.mkdir()
    for index, track_name in enumerate(track_names):
        metadata = build_track_metadata(disc, index, "Electronic")
        encode_track(sample_wav, str(album_dir / track_name), metadata)
    files = sorted(os.listdir(album_dir))
    assert len(files) == 10
    assert files[0] == "The Crystal Method - 01 - Trip Like I Do.flac"
    assert files[-1] == "The Crystal Method - 10 - Bad Stone.flac"


def test_encode_compilation_album(sample_wav, tmp_path):
    """Encode a compilation, verify per-track artists in tags."""
    disc = disc_by_artist("Various Artists")  # Forrest Gump
    folder, track_names = generate_filenames(disc)
    album_dir = tmp_path / folder
    album_dir.mkdir()
    for index, track_name in enumerate(track_names):
        metadata = build_track_metadata(disc, index, "Soundtrack")
        encode_track(sample_wav, str(album_dir / track_name), metadata)
    files = sorted(os.listdir(album_dir))
    assert len(files) == 16
    # Spot-check: first alphabetically is Alan Silvestri
    first = FLAC(str(album_dir / files[0]))
    assert first["albumartist"] == ["Various Artists"]
    assert first["artist"] == ["Alan Silvestri"]
