import os
import subprocess

from text_utils import clean, title_case, is_compilation, parse_compilation_track
from scan_disc import read_disc, query_gnudb, read_gnudb, search_musicbrainz
from encode import prompt_genre, build_track_metadata, encode_track


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


def rip_track(track_number, output_file):
    subprocess.run(["cdparanoia", str(track_number), output_file], check=True)


def rip_disc(output_dir):
    freedb_id, musicbrainz_id, num_tracks, offsets, total_sectors = read_disc()

    try:
        category, gnudb_id = query_gnudb(freedb_id, num_tracks, offsets, total_sectors)
        artist, album, year, genre, tracks = read_gnudb(category, gnudb_id)
        gnudb_ok = True
    except Exception as e:
        print(f"\nCould not read disc info from GnuDB: {e}")
        category, gnudb_id = "", ""
        artist, album, year, genre = "", "", "", ""
        tracks = [f"Track {i:02d}" for i in range(1, num_tracks + 1)]
        gnudb_ok = False

    disc_data = {
        "freedb_id": freedb_id,
        "musicbrainz_id": musicbrainz_id,
        "category": category,
        "artist": artist,
        "album": album,
        "year": year,
        "genre": genre,
        "num_tracks": num_tracks,
        "offsets": offsets,
        "tracks": tracks}

    print(f"\n{artist} - {album} ({year}) [{genre}] — {num_tracks} tracks\n")

    if not artist.strip():
        artist = input("Artist: ").strip()
        disc_data["artist"] = artist
        album = input("Album: ").strip()
        disc_data["album"] = album

    if not gnudb_ok:
        print("Searching MusicBrainz for track listing...")
        mb_tracks, mb_year = search_musicbrainz(artist, album)
        if mb_tracks:
            tracks = mb_tracks
            disc_data["tracks"] = tracks
            print(f"Found {len(tracks)} tracks on MusicBrainz.")
        else:
            print("No MusicBrainz results found; track names will be placeholders.")
        if mb_year and not year:
            year = mb_year
            disc_data["year"] = year

    if not year.strip():
        year = input("Year: ").strip()
        disc_data["year"] = year

    chosen_genre = prompt_genre(genre)

    folder, track_filenames = generate_filenames(disc_data)
    album_dir = os.path.join(output_dir, folder)
    os.makedirs(album_dir, exist_ok=True)

    for i, flac_name in enumerate(track_filenames, start=1):
        print(f"[{i}/{num_tracks}] Ripping {tracks[i-1]}...")
        wav_path = os.path.join(album_dir, f"track{i:02d}.wav")
        flac_path = os.path.join(album_dir, flac_name)
        rip_track(i, wav_path)
        metadata = build_track_metadata(disc_data, i - 1, chosen_genre)
        encode_track(wav_path, flac_path, metadata)
        os.remove(wav_path)

    print(f"\nDone: {album_dir}")
    subprocess.run(["eject", "/dev/cdrom"])


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Rip a CD to FLAC files with metadata from GnuDB.")
    parser.add_argument(
        "output_dir", nargs="?", default=".",
        help="directory to write album folder into (default: current directory)")
    args = parser.parse_args()
    rip_disc(args.output_dir)
