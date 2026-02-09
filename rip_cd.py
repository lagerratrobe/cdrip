import os
import subprocess
from mutagen.flac import FLAC


def clean(text):
    """Strip whitespace, carriage returns, and collapse double spaces."""
    return ' '.join(text.split())


def title_case(text):
    """Capitalize the first letter of each word, preserving internal casing."""
    def cap_word(word):
        for i, char in enumerate(word):
            if char.isalpha():
                return word[:i] + char.upper() + word[i+1:]
        return word
    return ' '.join(cap_word(word) for word in text.split(' '))


def is_compilation(artist):
    return clean(artist).lower() in ('various', 'various artists')


def parse_compilation_track(track_str):
    """Parse 'Artist / Title' or 'Artist - Title' from a compilation track."""
    track = clean(track_str)
    if ' / ' in track:
        artist, title = track.split(' / ', 1)
        return artist, title
    elif ' - ' in track:
        artist, title = track.split(' - ', 1)
        return artist, title
    return None, track


def generate_filenames(disc_data):
    """Generate folder name and track filenames from disc data.

    Returns (folder_name, [track_filenames])
    """
    artist = title_case(clean(disc_data['artist']))
    album = title_case(clean(disc_data['album']))

    if is_compilation(artist):
        folder_artist = "Various Artists"
    else:
        folder_artist = artist

    folder = f"{folder_artist} - {album}"

    track_files = []
    for i, track_str in enumerate(disc_data['tracks'], start=1):
        if is_compilation(artist):
            track_artist, title = parse_compilation_track(track_str)
            track_artist = title_case(clean(track_artist)) if track_artist else folder_artist
            title = title_case(clean(title))
        else:
            track_artist = artist
            title = title_case(clean(track_str))
        filename = f"{track_artist} - {i:02d} - {title}.flac"
        track_files.append(filename)

    return folder, track_files


if __name__ == "__main__":
    raw = ['John Doan - Amazing Grace (Part)\r',
           'Paul McCandless - Maria Walks Among the Thorns\r',
           'David Darling - Colorado Blue\r',
           'John Doan - Amazing Grace\r',
           'Will Ackerman - Impending Death of the Virgin Spirit\r',
           'Soulfood & Billy McLaughlin - The White Bear\r',
           'Tim Story - Caranna\r',
           "John Boswell - I'll Carry You Through\r",
           'John Boswell - Leaf Dream\r',
           'Liz Story - Blessings\r',
           'Bill Douglas - Autumn Song\r',
           'George Winston - What Are the Signs\r',
           "Michael Manring - Year's End\r"]

    tracks = [tuple(item.strip().split(" - ", 1)) for item in raw]

    album = "Best of Hearts of Space, No. 3 Innocence"
    year = "2009"
    genre = "New Age"
    output_dir = "./Scratch"

    os.makedirs(output_dir, exist_ok=True)

    for i, (artist, title) in enumerate(tracks, start=1):
        wav_file = os.path.join(output_dir, f"track{i:02d}.wav")
        flac_file = os.path.join(output_dir, f"{i:02d} - {artist} - {title}.flac")

        # Rip
        subprocess.run(["cdparanoia", str(i), wav_file], check=True)

        # Encode
        subprocess.run(["flac", "--best", "-o", flac_file, wav_file], check=True)

        # Tag
        audio = FLAC(flac_file)
        audio["title"] = title
        audio["artist"] = artist
        audio["album"] = album
        audio["albumartist"] = "Various"
        audio["date"] = year
        audio["genre"] = genre
        audio["tracknumber"] = str(i)
        audio["totaltracks"] = str(len(tracks))
        audio.save()

        # Clean up WAV
        os.remove(wav_file)
