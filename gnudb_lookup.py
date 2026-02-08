import discid
import urllib.request

# 1. Access the Disc
# Ensure a CD is in the drive before running this line
disc = discid.read("/dev/cdrom")
offsets = [track.offset for track in disc.tracks]
offset_str = "+".join(str(o) for o in offsets)
total_seconds = disc.sectors // 75

# 2. Construct and execute the Query URL
query_url = (
    f"http://gnudb.gnudb.org/~cddb/cddb.cgi"
    f"?cmd=cddb+query+{disc.freedb_id}+{len(disc.tracks)}"
    f"+{offset_str}+{total_seconds}"
    f"&hello=user+hostname+cdrip+0.1&proto=6"
)
req = urllib.request.Request(query_url)
response = urllib.request.urlopen(req)
query_result = response.read().decode("utf-8")

# 3. Parse Category and ID from Query Result
# This assumes a successful status code 200 for the first match
lines = query_result.strip().split("\n")
status_line = lines[1]
parts = status_line.split()
category = parts[0]
gnudb_id = parts[1]

# 4. Construct and execute the Read URL
read_url = (
    f"http://gnudb.gnudb.org/~cddb/cddb.cgi"
    f"?cmd=cddb+read+{category}+{gnudb_id}"
    f"&hello=user+hostname+cdrip+0.1&proto=6"
)
req_read = urllib.request.Request(read_url)
response_read = urllib.request.urlopen(req_read)
record = response_read.read().decode("utf-8")

# 5. Parse the Record into Fields
# Strips comments and splits into key=value pairs
record_lines = record.strip().split("\n")
data_lines = [line for line in record_lines if not line.startswith("#") and line.strip() and line != "."]
fields = {}
for line in data_lines[1:]:
    key, _, value = line.partition("=")
    fields[key] = value

# 6. Extract Metadata
dtitle = fields["DTITLE"]
artist, album = dtitle.split(" / ", 1)
year = fields.get("DYEAR", "")
genre = fields.get("DGENRE", "")

# 7. Extract Tracks
track_keys = sorted([k for k in fields.keys() if k.startswith("TTITLE")])
tracks = [fields[k] for k in track_keys]

# 8. Output results
print(f"Artist: {artist}")
print(f"Album: {album}")
print(f"Year: {year}")
print(f"Genre: {genre}")
print(f"Tracks: {tracks}")