# Vocal Separator 🎤

A small Python utility that turns a song into **vocals** and **instrumental accompaniment** for singing practice.

When learning a song by ear, instruments can make it difficult to hear the singer's melody. This project creates a vocal track to study and a backing track to sing over. This standalone project combines singing practice with a small, understandable Python workflow.

```text
Song.mp3 → Demucs audio model → vocals.wav
                            → instrumental.wav
```

## What it does

- Separates an MP3 or other supported audio file into two stereo WAV files.
- Processes audio locally, with no API key or per-song API fee.
- Creates a separate output folder for every run to preserve previous results.
- Checks the input path and FFmpeg installation before processing.
- Downloads model weights on the first run and reuses them afterward.

This first version is a command-line utility. A player, looping, playback-speed controls, and note detection are not implemented yet.

## How separation works

A mixed song does not contain independently retrievable studio tracks. [Demucs](https://github.com/facebookresearch/demucs) uses a pretrained neural network to estimate the audio sources. We use its `htdemucs` model and vocals-versus-accompaniment output mode.

Our Python code handles files and launches the model; Demucs performs the separation. No model training or language-model API is required. After dependencies and model weights are downloaded, processing can run offline.

## Requirements

The initial version was tested on an Apple Silicon Mac with:

- Python **3.12**
- [uv](https://docs.astral.sh/uv/) for Python environments and package installation
- [FFmpeg](https://ffmpeg.org/) available on your command-line `PATH`
- Internet access for initial dependency and model downloads

The model download is approximately **80 MB**, in addition to Python packages. Allow disk space for the environment, model cache, and uncompressed WAV outputs. A roughly five-minute song produces about 100 MB across the two WAV files.

Demucs's original repository is archived. The requirements pin Demucs and a matching Torch/Torchaudio pair to keep this example compatible; use the dedicated Python 3.12 environment below.

## Quick start

### 1. Get the repository

```sh
git clone https://github.com/bhargavamangalagiri/vocal-separtor.git
cd vocal-separtor
```

If you already have the repository, open a terminal in its root directory. All commands below run from there.

### 2. Install the tools and dependencies

On macOS with Homebrew:

```sh
brew install uv ffmpeg
```

Create an isolated environment and install the Python packages:

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

The commands use the environment's interpreter explicitly, so activation is unnecessary. Other platforms need their own FFmpeg installation; these shell examples target macOS/Linux, and other platforms have not been tested.

### 3. Separate a song

Replace the example path with your audio file. Keep the quotation marks around paths containing spaces.

```sh
.venv/bin/python separate.py "$HOME/Downloads/My Song.mp3"
```

You will see model-download progress on the first run, followed by separation progress and the paths to both outputs:

```text
outputs/
└── separation-<unique-id>/
    └── htdemucs/
        └── My Song/
            ├── vocals.wav
            └── instrumental.wav
```

Open either WAV file in your preferred audio player. Processing runs on the CPU and may take several minutes or longer depending on your computer and song length. The initial 4:54 sample took approximately two minutes to separate on the development machine; this is an example, not a performance guarantee.

### Optional commands

Choose another output directory:

```sh
.venv/bin/python separate.py "$HOME/Downloads/My Song.mp3" --output ./practice_tracks
```

Display help:

```sh
.venv/bin/python separate.py --help
```

Custom output directories are not automatically covered by this project's Git ignore rules. Keep generated audio outside version control.

## A simple practice routine

1. Listen to a short phrase in the original song.
2. Play the same phrase in `vocals.wav` and focus on the melody, timing, and phrasing.
3. Imitate the phrase with the vocal track as a guide.
4. Sing it over `instrumental.wav`.

Separation makes the voice easier to hear, but does **not** identify musical notes or assess your singing.

## Understanding the Python code

The implementation is in [`separate.py`](separate.py).

### 1. Read the command-line arguments

`main()` uses Python's `argparse` module to read the required `song` path and optional `--output` directory. It converts both into `Path` objects, similar to Java's filesystem `Path` objects.

The `if __name__ == "__main__":` guard starts `main()` when you run the file directly. Importing the file from another Python program does not start processing.

### 2. Validate the input and prepare output

`separate_song(song: Path, output: Path) -> Path` accepts two paths and returns the folder containing the results. These **type hints** document expected values; Python does not enforce them at runtime. The explicit `is_file()` check performs runtime validation.

The function checks for FFmpeg, creates the output directory, and uses `tempfile.mkdtemp()` to create a uniquely named run folder. Despite the module's name, that folder persists until you delete it.

### 3. Run the model

The `command` variable is a list of command-line arguments. `subprocess.run()` starts Demucs using `sys.executable`, the same Python interpreter running our script. Passing an argument list preserves spaces and punctuation in filenames without shell interpretation.

The main options are:

| Option | Purpose |
| --- | --- |
| `--two-stems vocals` | Produce vocals and the remaining accompaniment |
| `-n htdemucs` | Select the pretrained model |
| `-d cpu` | Use the CPU |
| `--shifts 1` | Use one random-shift prediction pass |
| `-j 1` | Use one processing job |
| `-o` | Choose the run's output directory |

`TORCH_HOME` directs the model cache into this project's `.cache/torch` folder. `check=True` makes `subprocess.run()` raise an exception if Demucs exits unsuccessfully.

### 4. Return the results

After processing, the function checks that both WAV files exist and renames Demucs's `no_vocals.wav` to `instrumental.wav`. It returns the folder, and `main()` prints the two paths.

Expected errors are caught and reported with a nonzero exit status. A failed run may leave a partial output folder for inspection; rerunning creates a fresh folder.

## Limitations

- These are estimated stems, not the original studio recordings.
- Instrument bleed, traces of vocals, and separation artifacts may remain.
- Backing vocals and harmonies may be included with the lead singer.
- WAV avoids another lossy MP3 encode but cannot restore information already lost in the input MP3.
- Automatic file checks do not establish listening quality. Compare a verse and chorus yourself.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| `Audio file not found` | Confirm the path and quote filenames containing spaces. |
| `FFmpeg is required` | Install FFmpeg and check that `ffmpeg -version` works in your terminal. |
| `No module named demucs` | Install requirements and use `.venv/bin/python`. |
| Model download fails | Check your internet connection and retry; the first run needs model weights. |
| Processing is slow | CPU processing takes time. Follow the progress bar and allow the run to finish. |
| Separation sounds imperfect | Compare different sections; quality depends on the mix and recording. |

## Project files

```text
vocal-separtor/
├── separate.py          # Command-line entry point and separation workflow
├── requirements.txt     # Python dependencies
├── README.md            # Setup, usage, and learning guide
├── .gitignore           # Excludes local/generated files
├── .venv/               # Local environment (not committed)
├── .cache/              # Downloaded model weights (not committed)
└── outputs/             # Separated audio (not committed)
```

The example song and generated stems are not included in the repository. Supply your own audio file.

## Validation and next steps

The first end-to-end run produced two readable, non-silent, finite-valued stereo WAV files at 44.1 kHz, each matching the sample's 294.441-second duration. Command-line help and missing-file handling were also checked. This verifies file generation, not separation quality.

Planned learning increments:

- A player for switching between the original, vocals, and accompaniment
- Phrase looping and pitch-preserving slow playback
- Adjustable vocal volume for gradually reducing guidance
- Optional pitch estimation to visualize the melody

## Acknowledgments

Built using [Demucs](https://github.com/facebookresearch/demucs), [PyTorch](https://pytorch.org/), and [FFmpeg](https://ffmpeg.org/). Their respective licenses and documentation apply to those dependencies.
