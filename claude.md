# cdrip - CD Ripping Tool

Python tool for ripping audio CDs with proper metadata tagging.

## Architecture
- Uses `discid` library to read CD disc IDs
- Queries gnudb.org (freedb protocol) for album metadata (artist, title, tracks, genre, year)
- Uses cdparanoia for ripping to WAV, then encodes to FLAC
- Genre data from gnudb needs normalization (inconsistent casing, bad values like "Data")

## Dependencies
- Python 3, discid, cdparanoia, flac
- gnudb.org for metadata (freedb CDDB protocol)

## Known Issues
- gnudb genre can be inconsistent (mixed case, slash-separated, bogus like "Data")
- Missing year on some albums
- Multiple disc ID matches possible
