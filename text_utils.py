def clean(text):
    """Strip whitespace, carriage returns, and collapse double spaces."""
    return ' '.join(text.split())


def sanitize_filename(text):
    """Replace characters that are illegal or problematic in filenames."""
    return text.replace('/', '-').replace('\x00', '')


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
