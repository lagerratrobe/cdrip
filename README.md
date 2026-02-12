# cdrip
Tools to rip and encode music CDs to FLAC.

## Usage

### Rip a CD

Insert a disc and run:

```bash
python rip_cd.py /path/to/music
```

This reads the disc, queries GnuDB for metadata, prompts you to pick a genre,
then rips and encodes each track to FLAC. The album folder is created under the
output directory (defaults to the current directory if omitted). The disc is
ejected when finished.

### Encode existing WAV files

Some CDs can't be ripped through the normal pipeline and end up as raw
`Track N.wav` files. Use `encode_wavs.py` to attach metadata and encode them.

**Step 1 — generate a metadata template:**

```bash
python encode_wavs.py init ./path/to/wavs/
```

This scans the folder for `Track N.wav` files and writes a
`disc_metadata.json` template into it.

**Step 2 — fill in metadata:**

Edit `disc_metadata.json` by hand — fill in artist, album, year, genre, and
track titles.

**Step 3 — encode:**

```bash
python encode_wavs.py encode ./path/to/wavs/ /path/to/music
```

This reads the metadata, prompts for genre confirmation, then encodes each WAV
to FLAC with tags. The album folder is created under the output directory
(defaults to the current directory if omitted).

### Scan a disc to test data

```bash
python scan_disc.py
```

Reads the current CD and appends its metadata to `tests/disc_data.json` for use
in tests.

## File naming

- Folder: `Artist - Album/`
- Tracks: `Artist - 01 - Title.flac`
- Compilations use `Various Artists` as the folder artist

## Test info

What is conftest.py?

This is a special pytest file — pytest automatically discovers it and makes its fixtures available to all test files
in the same directory. It contains:
- sys.path setup — adds the project root so from rip_cd import ... etc. work from inside tests/
- load_disc_data() — reads disc_data.json (was duplicated in both test files, now lives in one place)
- disc fixture — parametrized across all 11 discs. Any test function that takes disc as an argument automatically runs
once per disc.
- sample_wav fixture — provides the path to Track 1.wav, skipping if the file is missing.

### How to run tests:

* Run everything (117 tests)
`python -m pytest tests/`

* Verbose output (see each test name)
`python -m pytest tests/ -v`

* Run just filename tests
`python -m pytest tests/test_filenames.py`

* Run just encode tests
`python -m pytest tests/test_encode.py`

* Run a single test by name
`python -m pytest tests/ -k test_title_case`

