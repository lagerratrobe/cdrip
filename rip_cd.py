import os
import subprocess
from mutagen.flac import FLAC

raw = ['John Doan - Amazing Grace (Part)\r', 
       'Paul McCandless - Maria Walks Among the Thorns\r', 
       'David Darling - Colorado Blue\r', 
       'John Doan - Amazing Grace\r', 
       'Will Ackerman - Impending Death of the Virgin Spirit\r', 
       'Soulfood & Billy McLaughlin - The White Bear\r', 
       'Tim Story - Caranna\r', 
       "John Boswell - I'll Carry You Through\r", 
       'John Boswell - Leaf Dream\r', 
       'Liz Story - Blessings\r', 
       'Bill Douglas - Autumn Song\r', 
       'George Winston - What Are the Signs\r', 
       "Michael Manring - Year's End\r"]

tracks = [tuple(item.strip().split(" - ", 1)) for item in raw]

album = "Best of Hearts of Space, No. 3 Innocence"
year = "2009"
genre = "New Age"
output_dir = "./Scratch"

os.makedirs(output_dir, exist_ok=True)

for i, (artist, title) in enumerate(tracks, start=1):
    wav_file = os.path.join(output_dir, f"track{i:02d}.wav")
    flac_file = os.path.join(output_dir, f"{i:02d} - {artist} - {title}.flac")

    # Rip
    subprocess.run(["cdparanoia", str(i), wav_file], check=True)

    # Encode
    subprocess.run(["flac", "--best", "-o", flac_file, wav_file], check=True)

    # Tag
    audio = FLAC(flac_file)
    audio["title"] = title
    audio["artist"] = artist
    audio["album"] = album
    audio["albumartist"] = "Various"
    audio["date"] = year
    audio["genre"] = genre
    audio["tracknumber"] = str(i)
    audio["totaltracks"] = str(len(tracks))
    audio.save()

    # Clean up WAV
    os.remove(wav_file)