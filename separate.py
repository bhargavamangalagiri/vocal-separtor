"""Separate a song into vocals and accompaniment using local Demucs."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


PROJECT = Path(__file__).resolve().parent


def separate_song(song: Path, output: Path) -> Path:
    """Run Demucs and return the folder containing both WAV files."""
    song = song.expanduser().resolve()
    if not song.is_file():
        raise ValueError(f"Audio file not found: {song}")
    if shutil.which("ffmpeg") is None:
        raise ValueError("FFmpeg is required. On macOS, install with: brew install ffmpeg")

    # Give each run its own directory so previous stems are never overwritten.
    output = output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    run_folder = Path(tempfile.mkdtemp(prefix="separation-", dir=output))
    environment = os.environ.copy()
    environment["TORCH_HOME"] = str(PROJECT / ".cache" / "torch")
    command = [
        sys.executable, "-m", "demucs",
        "--two-stems", "vocals",
        "-n", "htdemucs",
        "-d", "cpu",
        "--shifts", "1",
        "-j", "1",
        "-o", str(run_folder),
        str(song),
    ]
    print("Separating locally. The first run downloads the model.", flush=True)
    subprocess.run(command, check=True, env=environment)
    stems = run_folder / "htdemucs" / song.stem
    vocals = stems / "vocals.wav"
    accompaniment = stems / "no_vocals.wav"
    if not vocals.is_file() or not accompaniment.is_file():
        raise RuntimeError(f"Demucs did not create both expected files in {stems}")
    accompaniment.rename(stems / "instrumental.wav")
    return stems


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("song", type=Path, help="Path to an MP3 or other audio file")
    parser.add_argument("--output", type=Path, default=PROJECT / "outputs")
    args = parser.parse_args()
    try:
        stems = separate_song(args.song, args.output)
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Separation failed: {error}\n")
    print(f"\nVocals: {stems / 'vocals.wav'}")
    print(f"Instrumental: {stems / 'instrumental.wav'}")


if __name__ == "__main__":
    main()
