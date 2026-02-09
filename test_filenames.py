import json
import pytest
from rip_cd import generate_filenames, is_compilation


def load_disc_data(filename="disc_data.json"):
    decoder = json.JSONDecoder()
    discs = []
    with open(filename) as f:
        content = f.read().strip()
    while content:
        obj, idx = decoder.raw_decode(content)
        discs.append(obj)
        content = content[idx:].strip()
    return discs


DISCS = load_disc_data()


def disc_label(disc):
    return f"{disc['artist'].strip()} - {disc['album'].strip()}"


@pytest.fixture(params=DISCS, ids=disc_label)
def disc(request):
    return request.param


def test_no_carriage_returns(disc):
    folder, tracks = generate_filenames(disc)
    assert '\r' not in folder, f"Folder has \\r: {folder!r}"
    for track in tracks:
        assert '\r' not in track, f"Track has \\r: {track!r}"


def test_folder_is_artist_dash_album(disc):
    folder, _ = generate_filenames(disc)
    parts = folder.split(' - ', 1)
    assert len(parts) == 2, f"Folder missing ' - ' separator: {folder}"
    assert parts[0].strip(), f"Empty artist in folder: {folder}"
    assert parts[1].strip(), f"Empty album in folder: {folder}"


def test_compilation_folder_says_various_artists(disc):
    if not is_compilation(disc['artist']):
        pytest.skip("not a compilation")
    folder, _ = generate_filenames(disc)
    assert folder.startswith("Various Artists - "), f"Compilation folder should start with 'Various Artists': {folder}"


def test_track_format(disc):
    """Each track should be 'Artist - NN - Title.flac'."""
    _, tracks = generate_filenames(disc)
    for track in tracks:
        assert track.endswith('.flac'), f"Missing .flac extension: {track}"
        stem = track[:-5]  # strip .flac
        parts = stem.split(' - ')
        assert len(parts) >= 3, f"Track doesn't match 'Artist - NN - Title' pattern: {track}"
        track_num = parts[1]
        assert track_num.isdigit() and len(track_num) == 2, f"Bad track number '{track_num}' in: {track}"


def test_no_unsafe_filesystem_chars(disc):
    unsafe = set('/:*?"<>|')
    folder, tracks = generate_filenames(disc)
    for char in unsafe:
        assert char not in folder, f"Folder contains '{char}': {folder}"
        for track in tracks:
            assert char not in track, f"Track contains '{char}': {track}"


def test_no_double_spaces(disc):
    folder, tracks = generate_filenames(disc)
    assert '  ' not in folder, f"Folder has double space: {folder}"
    for track in tracks:
        assert '  ' not in track, f"Track has double space: {track}"


def test_title_case(disc):
    """Album and track titles should have capitalized words."""
    folder, tracks = generate_filenames(disc)
    album_part = folder.split(' - ', 1)[1]
    for word in album_part.split():
        first_alpha = next((ch for ch in word if ch.isalpha()), None)
        if first_alpha:
            assert first_alpha == first_alpha.upper(), f"Lowercase word '{word}' in album: {album_part}"
    for track in tracks:
        title_part = track.rsplit('.flac', 1)[0].split(' - ', 2)[2]
        for word in title_part.split():
            first_alpha = next((ch for ch in word if ch.isalpha()), None)
            if first_alpha:
                assert first_alpha == first_alpha.upper(), f"Lowercase word '{word}' in track: {track}"
