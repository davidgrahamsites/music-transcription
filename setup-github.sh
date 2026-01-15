#!/bin/bash
# GitHub Setup Script for MelodyTranscriber

set -euo pipefail

echo "================================================"
echo "GitHub Setup for MelodyTranscriber"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "build.sh" ]; then
    echo "❌ Error: Must run from melody-transcription directory"
    exit 1
fi

# Check if git remote already exists
if git remote | grep -q "origin"; then
    echo "✅ Git remote 'origin' already exists:"
    git remote -v
    echo ""
    read -p "Remove and re-add? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote remove origin
    else
        echo "Keeping existing remote"
        exit 0
    fi
fi

# Get GitHub username
echo "Enter your GitHub username:"
read -r GITHUB_USER

# Get repository name (default: melody-transcription)
echo "Enter repository name (default: melody-transcription):"
read -r REPO_NAME
REPO_NAME=${REPO_NAME:-melody-transcription}

# Create GitHub repository URL
REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

echo ""
echo "This will add remote: $REPO_URL"
echo ""
echo "⚠️  IMPORTANT: You must create the repository on GitHub first!"
echo "   Go to: https://github.com/new"
echo "   Repository name: $REPO_NAME"
echo "   Make it public or private (your choice)"
echo "   Do NOT initialize with README (we already have one)"
echo ""
read -p "Have you created the repository on GitHub? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please create the repository first, then run this script again"
    exit 1
fi

# Add remote
echo "Adding remote..."
git remote add origin "$REPO_URL"

# Rename branch to main if needed
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Renaming branch $CURRENT_BRANCH → main..."
    git branch -M main
fi

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "================================================"
echo "✅ GitHub Setup Complete!"
echo "================================================"
echo ""
echo "Remote URL: $REPO_URL"
echo "Branch: main"
echo ""
echo "Next steps:"
echo "  1. Verify: git remote -v"
echo "  2. Build: ./build.sh"
echo ""
