import json
import os
import re

from rip_cd import generate_filenames
from encode import prompt_genre, build_track_metadata, encode_track


def find_wav_tracks(wav_folder):
    """Find Track N.wav files in folder, return sorted list of (number, path) tuples."""
    pattern = re.compile(r'^Track (\d+)\.wav$')
    tracks = []
    for filename in os.listdir(wav_folder):
        match = pattern.match(filename)
        if match:
            tracks.append((int(match.group(1)), filename))
    tracks.sort()
    return tracks


def init_metadata(wav_folder):
    """Write disc_metadata.json template into wav_folder."""
    tracks = find_wav_tracks(wav_folder)
    if not tracks:
        print(f"No 'Track N.wav' files found in {wav_folder}")
        return

    track_names = [f"Track {num}" for num, _ in tracks]
    metadata = {
        "artist": "",
        "album": "",
        "year": "",
        "genre": "",
        "tracks": track_names}

    metadata_path = os.path.join(wav_folder, "disc_metadata.json")
    with open(metadata_path, "w") as file:
        json.dump(metadata, file, indent=2)
        file.write("\n")

    print(f"Wrote {metadata_path} with {len(track_names)} tracks")
    print("Edit the file to fill in artist, album, year, genre, and track titles.")


def encode_folder(wav_folder, output_dir):
    """Encode wav folder to flac using metadata from disc_metadata.json."""
    metadata_path = os.path.join(wav_folder, "disc_metadata.json")
    with open(metadata_path) as file:
        disc_data = json.load(file)

    wav_tracks = find_wav_tracks(wav_folder)
    if len(wav_tracks) != len(disc_data['tracks']):
        print(f"Mismatch: {len(wav_tracks)} wav files vs {len(disc_data['tracks'])} tracks in metadata")
        return

    chosen_genre = prompt_genre(disc_data['genre'])
    folder, track_filenames = generate_filenames(disc_data)
    album_dir = os.path.join(output_dir, folder)
    os.makedirs(album_dir, exist_ok=True)

    num_tracks = len(wav_tracks)
    for index, (track_num, wav_name) in enumerate(wav_tracks):
        wav_path = os.path.join(wav_folder, wav_name)
        flac_path = os.path.join(album_dir, track_filenames[index])
        print(f"[{index + 1}/{num_tracks}] {track_filenames[index]}")
        metadata = build_track_metadata(disc_data, index, chosen_genre)
        encode_track(wav_path, flac_path, metadata)

    print(f"\nDone: {album_dir}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Encode a folder of WAV files to FLAC with metadata.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init", help="Create disc_metadata.json template in wav folder")
    init_parser.add_argument("wav_folder", help="folder containing Track N.wav files")

    encode_parser = subparsers.add_parser(
        "encode", help="Encode wav files to flac using disc_metadata.json")
    encode_parser.add_argument("wav_folder", help="folder containing Track N.wav files and disc_metadata.json")
    encode_parser.add_argument(
        "output_dir", nargs="?", default=".",
        help="directory to write album folder into (default: current directory)")

    args = parser.parse_args()
    if args.command == "init":
        init_metadata(args.wav_folder)
    elif args.command == "encode":
        encode_folder(args.wav_folder, args.output_dir)
