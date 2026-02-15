# EPUB to Anki Generator (Japanese)

This tool automatically converts Japanese **EPUB books** into organized **Anki Decks**. It reads the book chapter-by-chapter, extracts vocabulary, looks up definitions in **JMdict**, and creates a study deck that follows the book's progression.

## Features

- **Chapter-Based Subdecks:** Creates a separate deck for each chapter
- **Incremental Progression:** Words learned in Chapter 1 are **skipped** in Chapter 2
- **Smart Frequency Sorting:** Words are sorted by how often they appear
- **Context Sentences:** Extracts real example sentences from the dictionary
- **Clean Anki Cards:** Includes reading (furigana), meaning, and styling

---

## Quick Start

### Windows

1. **Double-click `setup.bat`** and follow the prompts
2. **Run the app:** Double-click `main.py` or run `python main.py` in terminal
3. **Import:** The script creates an `.apkg` file - double-click to import into Anki

### Mac / Linux

1. Open terminal in this folder
2. Run: `pip install -r requirements.txt`
3. Run: `./setup.sh` (or manually download the dictionary to `dict/` folder)
4. Run: `python main.py`

---

## Usage

1. Run the script: `python main.py`
2. Paste your EPUB path (drag and drop the file into terminal)
3. Choose: Include particles/grammar? (y/n)
   - `y`: Everything (desu, wa, ga, etc.)
   - `n`: Only content words (nouns, verbs, adjectives) - Recommended for vocab mining
4. The `.apkg` file is created in the same folder as your EPUB
5. Double-click to import into Anki

## Troubleshooting

**"Dictionary not found" Error**
- Did you run setup.bat/setup.sh? The dictionary file is needed in the `dict/` folder.

**"Python is not recognized" Error**
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

**Permission denied (Mac/Linux)**
- Run `chmod +x setup.sh` in terminal
