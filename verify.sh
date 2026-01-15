#!/bin/bash
set -euo pipefail

echo "================================================"
echo "MelodyTranscriber Verification Script"
echo "================================================"
echo ""

APP_PATH="dist/MelodyTranscriber.app"
EXEC_PATH="$APP_PATH/Contents/MacOS/MelodyTranscriber"

# 1. Check .app exists
echo "Check 1/5: .app bundle exists..."
if [[ ! -d "$APP_PATH" ]]; then
    echo "❌ .app bundle not found at: $APP_PATH"
    echo "   Please run ./build.sh first"
    exit 1
fi
echo "✅ .app bundle found"
echo ""

# 2. Check executable exists
echo "Check 2/5: Executable exists..."
if [[ ! -f "$EXEC_PATH" ]]; then
    echo "❌ Executable not found at: $EXEC_PATH"
    exit 1
fi
echo "✅ Executable found"
echo ""

# 3. Check architecture
echo "Check 3/5: Architecture check..."
ARCH_INFO=$(file "$EXEC_PATH")
echo "File info: $ARCH_INFO"

if echo "$ARCH_INFO" | grep -q "arm64"; then
    echo "✅ arm64 architecture confirmed"
else
    if echo "$ARCH_INFO" | grep -q "x86_64"; then
        echo "⚠️  WARNING: x86_64 architecture detected (not arm64)"
        echo "   This will run under Rosetta on Apple Silicon"
    else
        echo "❌ Unknown architecture"
        exit 1
    fi
fi
echo ""

# 4. Check dependencies
echo "Check 4/5: Dependency check..."
echo "Dynamic libraries:"
otool -L "$EXEC_PATH" | grep -v "^$EXEC_PATH" | head -20

echo ""
EXTERNAL_DEPS=$(otool -L "$EXEC_PATH" | grep -v '@rpath' | grep -v '/System' | grep -v '/usr/lib' | grep -v "^$EXEC_PATH" | wc -l)
if [ "$EXTERNAL_DEPS" -gt 0 ]; then
    echo "⚠️  WARNING: Found $EXTERNAL_DEPS external dependencies (should be bundled)"
    echo "External dependencies:"
    otool -L "$EXEC_PATH" | grep -v '@rpath' | grep -v '/System' | grep -v '/usr/lib' | grep -v "^$EXEC_PATH"
else
    echo "✅ No external dependencies detected (all bundled or system libraries)"
fi
echo ""

# 5. Check code signing
echo "Check 5/5: Code signing..."
if codesign -dv "$APP_PATH" 2>&1 | grep -q "Signature"; then
    echo "Code signing info:"
    codesign -dv "$APP_PATH" 2>&1 | grep -E "Identifier|Authority|Signature"
    echo "✅ Code signed"
else
    echo "⚠️  Not code-signed (expected for local development)"
    echo "   For distribution, you should sign the app with:"
    echo "   codesign --deep --force --sign \"Developer ID Application: YourName\" $APP_PATH"
fi
echo ""

# Summary
echo "================================================"
echo "Verification Summary"
echo "================================================"
echo "✅ Basic verification complete"
echo ""
echo "App info:"
if [ -f "$APP_PATH/Contents/Info.plist" ]; then
    echo "  Bundle ID: $(defaults read "$APP_PATH/Contents/Info.plist" CFBundleIdentifier 2>/dev/null || echo 'N/A')"
    echo echo "  Version:   $(defaults read "$APP_PATH/Contents/Info.plist" CFBundleShortVersionString 2>/dev/null || echo 'N/A')"
fi
echo ""
echo "Manual tests required:"
echo "  1. Double-click the .app to launch"
echo "  2. Test on a clean macOS system (no conda, no dev tools)"
echo "  3. Verify microphone permission prompt appears"
echo "  4. Test complete workflow: record → transcribe → export"
echo ""
echo "Files:"
echo "  App:  $APP_PATH"
echo "  Exec: $EXEC_PATH"
if [ -f "dist/MelodyTranscriber.dmg" ]; then
    DMG_SIZE=$(du -h "dist/MelodyTranscriber.dmg" | cut -f1)
    echo "  DMG:  dist/MelodyTranscriber.dmg ($DMG_SIZE)"
fi
echo ""
