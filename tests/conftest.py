import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

TEST_DIR = os.path.dirname(__file__)


def load_disc_data():
    decoder = json.JSONDecoder()
    discs = []
    with open(os.path.join(TEST_DIR, "disc_data.json")) as file:
        content = file.read().strip()
    while content:
        obj, idx = decoder.raw_decode(content)
        discs.append(obj)
        content = content[idx:].strip()
    return discs


DISCS = load_disc_data()


def disc_label(disc):
    return f"{disc['artist'].strip()} - {disc['album'].strip()}"


@pytest.fixture(params=DISCS, ids=disc_label)
def disc(request):
    return request.param


@pytest.fixture
def sample_wav():
    wav_file = os.path.join(TEST_DIR, "Track 1.wav")
    if not os.path.exists(wav_file):
        pytest.skip("Track 1.wav not found in tests/")
    return wav_file
