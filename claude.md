# cdrip - CD Ripping Tool

Python tool for ripping audio CDs with proper metadata tagging.
## Coding Style Preferences
- Keep __main__ clean: mostly just a sequence of function calls, no inline logic or formatting.
- Minimal exception handling: use broad `except Exception as e` only when graceful failure is needed; otherwise let Python's default traceback do the work
- Closing parens go on the last argument line, not on their own line
- Build iteratively: one function at a time, test before moving on
- Single file with functions, not multi-file module splits (unless the project outgrows it)

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
