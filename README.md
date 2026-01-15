# MelodyTranscriber

A macOS application that converts sung or hummed melodies into professional musical notation.

## Features

- 🎤 High-quality audio recording with real-time level monitoring
- 🎵 Advanced pitch detection using CREPE neural network
- 📊 Intelligent rhythm quantization with tempo and time signature control
- 🎼 Support for 100+ instruments including transposing instruments
- 🎹 Automatic key detection with manual override
- 📝 Export to MusicXML and MIDI formats
- ✏️ Basic notation editing (nudge, duration, delete)
- 🎯 Confidence scoring for transcription quality

## System Requirements

- macOS 11.0 or later (Apple Silicon / M1+)
- Microphone access

## Development Setup

### Prerequisites

- Conda (Miniconda or Anaconda)
- Git
- Xcode Command Line Tools

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd melody-transcription
```

2. Create the Conda environment:
```bash
conda env create -f environment.yml
conda activate melody-transcription
```

3. Run the application in development mode:
```bash
python src/main.py
```

## Building for Distribution

### Build the .app bundle

```bash
./build.sh
```

This will:
1. Verify Git status (clean working tree, all changes pushed)
2. Create a local backup
3. Bundle the application with PyInstaller
4. Create a distributable .dmg file

Output: `dist/MelodyTranscriber.dmg`

### Verification

```bash
./verify.sh
```

Checks:
- arm64 architecture
- Bundled dependencies
- Code signing status

## Usage

1. Launch MelodyTranscriber.app
2. Select your target instrument
3. Set tempo and time signature
4. Click Record and sing/hum your melody
5. Review and edit the generated notation
6. Export to MusicXML or MIDI

## Architecture

- **Audio Engine**: librosa, crepe, sounddevice
- **Notation**: music21
- **UI**: PySide6 (Qt6)
- **Packaging**: PyInstaller

## License

[Your License Here]

## Version

Built with Git commit: [Auto-generated during build]
