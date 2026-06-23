# HonToAnki

Convert Japanese EPUB books into Anki flashcard decks. Extracts vocabulary chapter-by-chapter, looks up definitions from JMdict, and generates organized Anki decks that follow the book's progression.

## Features

- **Chapter-based subdecks** -- each book chapter becomes a separate subdeck
- **Incremental learning** -- words already seen in earlier chapters are skipped in later ones
- **Frequency sorting** -- words within each chapter are ordered by occurrence count
- **Dictionary lookup** -- automatically downloads JMdict on first run (English includes example sentences)
- **Multi-language support** -- Japanese definitions available in 9 languages: English, Spanish, French, German, Russian, Dutch, Hungarian, Swedish, Slovenian
- **Headless mode** -- CLI flags for scripting and automation
- **Self-contained** -- no external dependencies for end users (pre-built binaries available)

## Quick Start

### Pre-built binary

Download the latest release for your platform from the [Releases](https://github.com/shaqu/hontoanki/releases) page.

| Platform | Installer | Portable |
|----------|-----------|----------|
| Windows | HonToAnki.msi (adds to PATH) | HonToAnki.zip (unzip and run) |
| macOS | HonToAnki.pkg (adds to PATH) | HonToAnki.zip (unzip and run) |
| Linux | .deb / .rpm | HonToAnki.AppImage |

Run `hontoanki` from your terminal. On first run, the JMdict dictionary downloads automatically (~120 MB for English).

### Running from source

Requires Python 3.11+ and pip:

```bash
git clone <repo>
cd HonToAnki
pip install -e .
hontoanki --epub book.epub
```

To install with dev dependencies (testing, building):

```bash
pip install -e ".[dev]"
```

## Usage

### Interactive mode

```
hontoanki
```

Prompts you for:
1. Dictionary language (defaults to English, persists via `--set-default-lang`)
2. EPUB file path
3. Whether to include particles and grammar words

### Headless mode

```
hontoanki --epub book.epub --lang spa
hontoanki --epub book.epub --lang ger --particles --output ./my_decks --json
```

Options:

| Flag | Description |
|------|-------------|
| `-e, --epub PATH` | EPUB file path (enables headless mode) |
| `-l, --lang CODE` | Dictionary language code (eng, spa, fre, ger, rus, dut, hun, swe, slv) |
| `-p, --particles` | Include particles and grammar words |
| `-o, --output DIR` | Output directory (default: ./exports) |
| `-j, --json` | Also export vocabulary as JSON |
| `--download-lang, --dl CODE` | Download dictionary for a language and exit |
| `--set-default-lang CODE` | Persist default language for future runs |
| `-v, --verbose` | Show detailed parsing info |

### Managing dictionaries

```bash
# Download Spanish dictionary (one-time, cached)
hontoanki --download-lang spa

# Set German as default language
hontoanki --set-default-lang ger

# Download Spanish and set it as default
hontoanki --dl spa --set-default-lang spa
```

Dictionaries are stored in the platform data directory:
- Windows: `%APPDATA%/HonToAnki/dict/{lang}/`
- macOS: `~/Library/Application Support/HonToAnki/dict/{lang}/`
- Linux: `~/.local/share/HonToAnki/dict/{lang}/`

### Building from source

```bash
# Install Briefcase
pip install briefcase

# Build all platforms
python build.py all

# Build portable ZIP for current platform
python build.py portable

# Build for a specific platform
python build.py windows
python build.py macos
python build.py linux
```

## Card Format

Each Anki card displays:

- **Front:** The word in Japanese
- **Back:** Reading (furigana), meaning (in the selected language), example sentence (English only), and chapter frequency tag

## Troubleshooting

**Dictionary download fails** -- Check your internet connection. The GitHub release redirect endpoint has generous rate limits, but the API fallback is restricted to 60 requests per hour for unauthenticated users.

**No Japanese content found** -- Ensure the EPUB contains Japanese text. Some EPUBs use image-based content that cannot be parsed. Try a different EPUB file.

**Build errors** -- Ensure Briefcase 0.4.2+ is installed. Windows builds require WiX Toolset; macOS builds require Xcode.

## License

MIT