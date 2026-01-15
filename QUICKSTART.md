# Quick Start Guide

## Prerequisites

1. **Install Conda/Miniconda** (if not already installed):
   ```bash
   # Download from: https://docs.conda.io/en/latest/miniconda.html
   # Or via Homebrew:
   brew install miniconda
   ```

2. **Install Git** (if not already installed):
   ```bash
   brew install git
   ```

## Setup (First Time)

1. **Navigate to project directory**:
   ```bash
   cd "/Volumes/Daniel K1/Antigravity/melody-transcription"
   ```

2. **Create Conda environment**:
   ```bash
   conda env create -f environment.yml
   ```
   
   This will install:
   - Python 3.11
   - Audio processing libraries (librosa, sounddevice, crepe)
   - Music notation library (music21)
   - UI framework (PySide6/Qt6)
   - Build tools (PyInstaller)
   
   ⏱️  This may take 5-10 minutes on first install.

3. **Activate environment**:
   ```bash
   conda activate melody-transcription
   ```

## Development Mode

To run the app in development mode (no build required):

```bash
cd "/Volumes/Daniel K1/Antigravity/melody-transcription"
conda activate melody-transcription
python src/main.py
```

The app will launch in a window. You can:
- Select an instrument
- Record your singing/humming
- Transcribe to notation
- Export to MusicXML or MIDI

## Building the .app

**IMPORTANT**: Before building, ensure all changes are committed AND pushed to GitHub.

1. **Commit your changes**:
   ```bash
   git add -A
   git commit -m "Your commit message"
   ```

2. **Push to remote** (REQUIRED):
   ```bash
   # First time: add remote if not already added
   git remote add origin https://github.com/YOUR_USERNAME/melody-transcription.git
   
   # Push
   git push -u origin master
   ```

3. **Run build script**:
   ```bash
   ./build.sh
   ```
   
   The build script will:
   - ✅ Verify Git status (clean + pushed)
   - ✅ Create automatic backup
   - ✅ Inject Git commit hash
   - ✅ Bundle app with PyInstaller
   - ✅ Create .dmg distributable
   
   **Build will FAIL if:**
   - Uncommitted changes exist
   - Local commits are not pushed to remote
   - Conda environment is not activated

4. **Verify the build**:
   ```bash
   ./verify.sh
   ```
   
   This checks:
   - arm64 architecture ✅
   - No missing dependencies
   - Code signing status

5. **Test the .app**:
   ```bash
   open dist/MelodyTranscriber.app
   ```

## Distributing

**Output files**:
- `dist/MelodyTranscriber.app` - Double-clickable app bundle
- `dist/MelodyTranscriber.dmg` - Distributable disk image

To distribute:
1. Share the `.dmg` file
2. Recipients can drag the .app to their Applications folder
3. On first launch, they may need to right-click → Open (to bypass Gatekeeper)

## Troubleshooting

### "conda: command not found"
```bash
# Initialize conda for your shell
conda init zsh  # or bash
# Restart your terminal
```

### "Environment not found"
```bash
# Recreate environment
conda env remove -n melody-transcription
conda env create -f environment.yml
```

### Build fails with "working tree is dirty"
```bash
# Check what's uncommitted
git status

# Commit everything
git add -A
git commit -m "Pre-build commit"
git push
```

### App crashes on launch
```bash
# Check dependencies
./verify.sh

# Run in development mode to see error
conda activate melody-transcription
python src/main.py
```

### Microphone not working
- Check System Preferences → Security & Privacy → Microphone
- Grant permission to Terminal (for dev mode) or MelodyTranscriber (for .app)

## Development Tips

### Add new instruments
Edit `src/data/instruments.json` and add entries following the existing format.

### Modify UI
Edit `src/ui/main_window.py`.

### Change audio processing
- Pitch detection: `src/audio/pitch_detector.py`
- Rhythm: `src/audio/rhythm_quantizer.py`
- Key detection: `src/audio/key_detector.py`

### Update dependencies
```bash
# Edit environment.yml
# Then recreate environment
conda env update -f environment.yml --prune
```

## Clean Up

To remove build artifacts:
```bash
rm -rf build dist
```

To remove the Conda environment:
```bash
conda deactivate
conda env remove -n melody-transcription
```
