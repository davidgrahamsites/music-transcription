#!/bin/bash
set -euo pipefail

echo "================================================"
echo "MelodyTranscriber Build Script"
echo "================================================"
echo ""

# 1. Check Git status
echo "Step 1/8: Checking Git status..."
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "❌ ERROR: Working tree is dirty. Commit changes first."
    echo "Uncommitted changes detected:"
    git status --short
    exit 1
fi

# Check if we have a remote
if git remote -v | grep -q 'origin'; then
    # Get current branch
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    
    # Check if local is ahead of remote
    LOCAL_HASH=$(git rev-parse @)
    REMOTE_HASH=$(git rev-parse @{u} 2>/dev/null || echo "")
    
    if [ -n "$REMOTE_HASH" ] && [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
        if ! git merge-base --is-ancestor @{u} @; then
            echo "❌ ERROR: Local branch is behind remote. Pull first."
            exit 1
        fi
        
        echo "❌ ERROR: Local commits not pushed. Push to remote first."
        echo "Branch: $CURRENT_BRANCH"
        echo "Run: git push origin $CURRENT_BRANCH"
        exit 1
    fi
else
    echo "⚠️  WARNING: No remote repository configured."
    echo "   Skipping push check, but local backup will still be created."
fi

echo "✅ Git status OK"
echo ""

# 2. Get Git commit hash
echo "Step 2/8: Getting Git commit hash..."
GIT_HASH=$(git rev-parse --short HEAD)
echo "Building with commit: $GIT_HASH"
echo ""

# 3. Create local backup
echo "Step 3/8: Creating local backup..."
BACKUP_DIR="backups/build_${GIT_HASH}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
rsync -a --exclude='.git' --exclude='dist' --exclude='build' --exclude='backups' --exclude='__pycache__' --exclude='*.pyc' . "$BACKUP_DIR/"
echo "✅ Backup created: $BACKUP_DIR"
echo ""

# 4. Clean build directory
echo "Step 4/8: Cleaning build directories..."
rm -rf build dist
echo "✅ Build directories cleaned"
echo ""

# 5. Check/activate Conda environment
echo "Step 5/8: Activating Conda environment..."
if ! command -v conda &> /dev/null; then
    echo "❌ ERROR: Conda not found. Please install Conda first."
    exit 1
fi

# Source conda properly
source ~/miniforge3/etc/profile.d/conda.sh || source ~/anaconda3/etc/profile.d/conda.sh || source ~/miniconda3/etc/profile.d/conda.sh

if ! conda env list | grep -q "^melody-transcription "; then
    echo "❌ ERROR: Conda environment 'melody-transcription' not found."
    echo "Please create it first with: conda env create -f environment.yml"
    exit 1
fi

conda activate melody-transcription
echo "✅ Conda environment activated"
echo ""

# 6. Inject Git hash into version file
echo "Step 6/8: Injecting Git commit hash..."
echo "GIT_COMMIT = '$GIT_HASH'" > src/utils/git_version.py
echo "✅ Git hash injected"
echo ""

# 7. Run PyInstaller
echo "Step 7/8: Running PyInstaller..."
pyinstaller --clean pyinstaller.spec
if [ $? -ne 0 ]; then
    echo "❌ ERROR: PyInstaller failed"
    exit 1
fi
echo "✅ PyInstaller completed"
echo ""

# 8. Create DMG (requires create-dmg to be installed)
echo "Step 8/8: Creating DMG..."
if command -v create-dmg &> /dev/null; then
    # Remove old DMG if exists
    rm -f "dist/MelodyTranscriber.dmg"
    
    create-dmg \
        --volname "MelodyTranscriber" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --app-drop-link 425 120 \
        "dist/MelodyTranscriber.dmg" \
        "dist/MelodyTranscriber.app" 2>/dev/null || {
            echo "⚠️  create-dmg failed, creating simple DMG..."
            hdiutil create -volname "MelodyTranscriber" -srcfolder "dist/MelodyTranscriber.app" -ov -format UDZO "dist/MelodyTranscriber.dmg"
        }
    echo "✅ DMG created"
else
    echo "⚠️  create-dmg not installed, creating simple DMG..."
    hdiutil create -volname "MelodyTranscriber" -srcfolder "dist/MelodyTranscriber.app" -ov -format UDZO "dist/MelodyTranscriber.dmg"
    echo "✅ Simple DMG created"
fi
echo ""

echo "================================================"
echo "✅ Build complete!"
echo "================================================"
echo ""
echo "Outputs:"
echo "  - App bundle:  dist/MelodyTranscriber.app"
echo "  - DMG file:    dist/MelodyTranscriber.dmg"
echo "  - Git commit:  $GIT_HASH"
echo "  - Backup:      $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "  1. Run ./verify.sh to verify the build"
echo "  2. Test the .app by double-clicking it"
echo "  3. Distribute the .dmg file"
echo ""
