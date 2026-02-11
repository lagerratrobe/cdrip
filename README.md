# cdrip
Tools to work with music CDs.


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

