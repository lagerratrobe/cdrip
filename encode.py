import subprocess
from mutagen.flac import FLAC
from text_utils import clean, title_case, is_compilation, parse_compilation_track


BOGUS_GENRES = {'data', 'other'}

GENRES = [
    'Rock', 'Pop', 'Alternative', 'Metal', 'Punk',
    'Hip-Hop', 'R&B / Soul', 'Funk', 'Jazz', 'Blues',
    'Classical', 'Country', 'Folk', 'Electronic', 'Reggae',
    'Latin', 'World', 'New Age', 'Bluegrass', 'Soundtrack', 'Other']

GENRE_ALIASES = {
    'techno': 'Electronic',
    'electronica': 'Electronic',
    'edm': 'Electronic',
    'dance': 'Electronic',
    'house': 'Electronic',
    'trance': 'Electronic',
    'ambient': 'Electronic',
    'drum and bass': 'Electronic',
    'drum & bass': 'Electronic',
    'dnb': 'Electronic',
    'idm': 'Electronic',
    'synthpop': 'Electronic',
    'downtempo': 'Electronic',
    'trip hop': 'Electronic',
    'trip-hop': 'Electronic',
    'r&b': 'R&B / Soul',
    'rnb': 'R&B / Soul',
    'soul': 'R&B / Soul',
    'motown': 'R&B / Soul',
    'rap': 'Hip-Hop',
    'hip hop': 'Hip-Hop',
    'hard rock': 'Rock',
    'classic rock': 'Rock',
    'prog rock': 'Rock',
    'progressive rock': 'Rock',
    'pop rock': 'Rock',
    'indie': 'Alternative',
    'indie rock': 'Alternative',
    'indie pop': 'Alternative',
    'grunge': 'Alternative',
    'shoegaze': 'Alternative',
    'post-punk': 'Alternative',
    'new wave': 'Alternative',
    'heavy metal': 'Metal',
    'thrash metal': 'Metal',
    'death metal': 'Metal',
    'black metal': 'Metal',
    'doom metal': 'Metal',
    'hardcore': 'Punk',
    'hardcore punk': 'Punk',
    'ska': 'Punk',
    'ska punk': 'Punk',
    'bluegrass': 'Bluegrass',
    'americana': 'Country',
    'bossa nova': 'Latin',
    'salsa': 'Latin',
    'samba': 'Latin',
    'afrobeat': 'World',
    'celtic': 'World',
    'flamenco': 'World',
    'gospel': 'Folk',
    'singer-songwriter': 'Folk',
    'soundtrack': 'Soundtrack'}


def clean_genre(genre):
    """Normalize genre: title case, strip bogus values."""
    genre = ' '.join(genre.split())
    if genre.lower() in BOGUS_GENRES:
        return ''
    parts = genre.split('/')
    return '/'.join(part.strip().title() for part in parts)


def suggest_genre(gnudb_genre):
    """Suggest a genre from GENRES based on gnudb genre string. Returns None if no match."""
    raw = ' '.join(gnudb_genre.split()).strip()
    if not raw or raw.lower() in BOGUS_GENRES:
        return None
    genres_lower = {genre.lower(): genre for genre in GENRES}
    if raw.lower() in genres_lower:
        return genres_lower[raw.lower()]
    if raw.lower() in GENRE_ALIASES:
        return GENRE_ALIASES[raw.lower()]
    first_part = raw.split('/')[0].strip()
    if first_part.lower() in genres_lower:
        return genres_lower[first_part.lower()]
    if first_part.lower() in GENRE_ALIASES:
        return GENRE_ALIASES[first_part.lower()]
    for genre in GENRES:
        if genre.lower() in raw.lower():
            return genre
    return None


def prompt_genre(gnudb_genre):
    """Interactive genre prompt. Shows gnudb genre as hint, pre-selects suggestion."""
    suggestion = suggest_genre(gnudb_genre)
    default_num = GENRES.index(suggestion) + 1 if suggestion else None

    print(f'\ngnudb genre: "{gnudb_genre}"\n')
    for row in range(7):
        parts = []
        for col in range(3):
            idx = row + col * 7
            if idx < len(GENRES):
                parts.append(f"{idx + 1:>2}) {GENRES[idx]:<13}")
        print("  ".join(parts))

    prompt_text = f"\nGenre [{default_num}]: " if default_num else "\nGenre: "
    while True:
        choice = input(prompt_text).strip()
        if not choice and default_num:
            return suggestion
        if choice.isdigit() and 1 <= int(choice) <= len(GENRES):
            picked = GENRES[int(choice) - 1]
            if picked == 'Other':
                return input("Enter genre: ").strip()
            return picked
        print(f"Enter a number from 1 to {len(GENRES)}")


def build_track_metadata(disc_data, track_index, genre):
    """Build metadata dict for track at given index (0-based)."""
    artist = title_case(clean(disc_data['artist']))
    album = title_case(clean(disc_data['album']))
    year = clean(disc_data.get('year', ''))
    tracks = disc_data['tracks']

    if is_compilation(disc_data['artist']):
        album_artist = "Various Artists"
        track_artist, title = parse_compilation_track(tracks[track_index])
        track_artist = title_case(clean(track_artist)) if track_artist else album_artist
        title = title_case(clean(title))
    else:
        album_artist = artist
        track_artist = artist
        title = title_case(clean(tracks[track_index]))

    return {
        "title": title,
        "artist": track_artist,
        "album": album,
        "albumartist": album_artist,
        "date": year,
        "genre": genre,
        "tracknumber": str(track_index + 1),
        "totaltracks": str(len(tracks))}


def encode_track(wav_file, flac_file, metadata):
    """Encode WAV to FLAC and apply metadata tags."""
    subprocess.run(["flac", "--best", "-o", flac_file, wav_file],
                   check=True, capture_output=True)
    audio = FLAC(flac_file)
    for key, value in metadata.items():
        if value:
            audio[key] = value
    audio.save()
