import json
import time
import discid
import urllib.request
import urllib.parse


def read_disc():
    disc = discid.read("/dev/cdrom")
    offsets = [track.offset for track in disc.tracks]
    return disc.freedb_id, disc.id, len(disc.tracks), offsets, disc.sectors


def query_gnudb(freedb_id, num_tracks, offsets, total_sectors):
    offset_str = "+".join(str(o) for o in offsets)
    total_seconds = total_sectors // 75
    query_url = (
        f"http://gnudb.gnudb.org/~cddb/cddb.cgi"
        f"?cmd=cddb+query+{freedb_id}+{num_tracks}"
        f"+{offset_str}+{total_seconds}"
        f"&hello=user+hostname+cdrip+0.1&proto=6")
    req = urllib.request.Request(query_url)
    response = urllib.request.urlopen(req)
    query_result = response.read().decode("utf-8")
    lines = query_result.strip().split("\n")
    status_line = lines[1]
    parts = status_line.split()
    category = parts[0]
    gnudb_id = parts[1]
    return category, gnudb_id


def read_gnudb(category, gnudb_id):
    read_url = (
        f"http://gnudb.gnudb.org/~cddb/cddb.cgi"
        f"?cmd=cddb+read+{category}+{gnudb_id}"
        f"&hello=user+hostname+cdrip+0.1&proto=6")
    req = urllib.request.Request(read_url)
    response = urllib.request.urlopen(req)
    record = response.read().decode("utf-8")
    record_lines = record.strip().split("\n")
    data_lines = [line for line in record_lines
                  if not line.startswith("#") and line.strip() and line != "."]
    fields = {}
    for line in data_lines[1:]:
        key, _, value = line.partition("=")
        fields[key] = value
    dtitle = fields["DTITLE"].strip()
    if " / " in dtitle:
        artist, album = dtitle.split(" / ", 1)
    else:
        artist, album = "", dtitle
    year = fields.get("DYEAR", "").strip()
    genre = fields.get("DGENRE", "").strip()
    track_keys = sorted([k for k in fields if k.startswith("TTITLE")],
                        key=lambda k: int(k[6:]))
    tracks = [fields[k].strip() for k in track_keys]
    return artist, album, year, genre, tracks


def search_musicbrainz(artist, album):
    """Search MusicBrainz for a release by artist and album.

    Returns (tracks, year) on success, or (None, None) if nothing found.
    """
    base = "https://musicbrainz.org/ws/2"
    headers = {"User-Agent": "cdrip/0.1 (https://github.com/lagerratrobe/cdrip)"}

    query = f'artist:"{artist}" AND release:"{album}"'
    search_url = f"{base}/release?query={urllib.parse.quote(query)}&fmt=json&limit=1"
    req = urllib.request.Request(search_url, headers=headers)
    response = urllib.request.urlopen(req)
    data = json.loads(response.read().decode("utf-8"))

    releases = data.get("releases", [])
    if not releases:
        return None, None

    mbid = releases[0]["id"]
    year = releases[0].get("date", "")[:4]

    time.sleep(1)  # MusicBrainz rate limit

    release_url = f"{base}/release/{mbid}?inc=recordings&fmt=json"
    req = urllib.request.Request(release_url, headers=headers)
    response = urllib.request.urlopen(req)
    release = json.loads(response.read().decode("utf-8"))

    tracks = []
    for medium in release.get("media", []):
        for track in medium.get("tracks", []):
            tracks.append(track["title"])

    return tracks, year


def append_to_file(data, filename="disc_data.json"):
    with open(filename, "a") as f:
        f.write(json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    freedb_id, musicbrainz_id, num_tracks, offsets, total_sectors = read_disc()
    category, gnudb_id = query_gnudb(freedb_id, num_tracks, offsets, total_sectors)
    artist, album, year, genre, tracks = read_gnudb(category, gnudb_id)

    data = {
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

    append_to_file(data)
    print(f"{artist} - {album} ({year}) [{genre}] — {num_tracks} tracks")
    print(f"  Saved to disc_data.json")

    import subprocess
    subprocess.run(["eject", "/dev/cdrom"])
