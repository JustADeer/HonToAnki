# 📚 EPUB to Anki Generator (Japanese)

This tool automatically converts Japanese **EPUB books** into organized **Anki Decks**. It reads the book chapter-by-chapter, extracts vocabulary, looks up definitions in **JMdict**, and creates a study deck that follows the book's progression.

## Features

- **Chapter-Based Subdecks:** Creates a separate deck for each chapter (e.g., `Book::01_Chapter 1`, `Book::02_Chapter 2`).
- **Incremental Progression:** Words learned in Chapter 1 are **skipped** in Chapter 2. You only study _new_ words for each section.
- **Smart Frequency Sorting:** Words are sorted by how often they appear in that specific chapter.
- **Context Sentences:** Extracts real example sentences from the dictionary.
- **Clean Anki Cards:** Includes reading (furigana), meaning, and styling.

---

## Quick Start (Read This First!)

Before running the python script, you **must** run the setup script. This downloads the necessary Japanese dictionary and installs dependencies.

### 1. Prerequisites

You will need [uv](https://github.com/astral-sh/uv) installed to manage dependencies and the python environment.

**MacOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Or, from PyPI:**

```
pip install uv
```

### 2. Run Setup

Run the `setup.sh` script. This will download the latest JMdict (English-Japanese) dictionary and install all Python libraries.

**MacOS/Linux:**

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup
./setup.sh
```

**Windows Users**: You can run the above command using Git Bash. If you do not have Git Bash:

1. Manually create a folder named `dict`.
2. Download the `jmdict-examples-eng-3.6.2.json` file and place it inside.
3. Run `uv sync` in your terminal.

## Usage Once the setup is complete, you can generate your Anki deck.

### 1. Run the script:

```bash
uv run main.py
```

### 2. Paste your EPUB path: The script will ask for the location of your book. You can drag and drop the file into the terminal.

```
Paste .epub Book Path: "C:\Books\MyJapaneseBook.epub"
```

### 3. Select Options:

- Include particles/grammar? (y/n):
  - `y`: Extracts everything (Desu, Wa, Ga, etc.).
  - `n`: Extracts only Content Words (Nouns, Verbs, Adjectives). Recommended for Vocab Mining.

### 4. Import to Anki:

- The script creates an .apkg file in the same folder as your EPUB.
- Double-click the file to import it into Anki.
- The decks will automatically organize themselves into a folder structure.

## Project Structure

```
.
├── dict/                   # Created by setup.sh (contains dictionary JSON)
├── main.py                 # The magic logic
├── setup.sh                # run this FIRST!
├── pyproject.toml          # Dependency list
└── README.md               # You are here
```

### Troubleshooting

**"Dictionary not found" Error**

- Did you run ./setup.sh? The script needs the JSON dictionary file in the dict/ folder to look up words.

**The Chapter Names look weird (e.g., "Section p-0012")**

- This happens if the EPUB does not have a Table of Contents (TOC). The script tries to fall back to HTML headers, but if those are missing too, it uses the internal file ID to ensure no data is lost.

**I see "Permission denied" when running setup.sh**

- Run chmod +x setup.sh in your terminal to give it run permissions.
