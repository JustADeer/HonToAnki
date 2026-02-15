#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

REPO="scriptin/jmdict-simplified"        # e.g. wordset/dictionary
DEST_DIR="dict"

API_URL="https://api.github.com/repos/$REPO/releases/latest"

echo "Fetching latest release info..."
DOWNLOAD_URL=$(
  curl -s "$API_URL" |
    grep '"browser_download_url"' |
    grep 'jmdict-examples-eng-.*\.json\.zip"' |
    head -n 1 |
    cut -d '"' -f 4
)

if [ -z "$DOWNLOAD_URL" ]; then
  echo "Error: could not find matching asset"
  exit 1
fi

echo "Downloading $DOWNLOAD_URL"
mkdir -p "$DEST_DIR"
curl -L "$DOWNLOAD_URL" -o dict.zip

echo "Extracting..."
unzip -o dict.zip -d "$DEST_DIR"

echo "Cleaning up..."
rm dict.zip

echo "Initializing dependencies"
if command -v uv &> /dev/null; then
    uv sync
elif command -v pip &> /dev/null; then
    pip install -r requirements.txt
else
    echo "Error: Neither uv nor pip found. Please install Python from https://python.org"
    exit 1
fi

echo "Done."
