# EPUB to Anki Generator (Japanese)

This tool automatically converts Japanese **EPUB books** into organized **Anki Decks**. It reads the book chapter-by-chapter, extracts vocabulary, looks up definitions in **JMdict**, and creates a study deck that follows the book's progression.

<<<<<<< HEAD
### Notice!!!
I am currently working on a `cli` and also an `app w/ UI` based design of this project. Both of them will be written in `rust` and the app version will use `Tauri` as the framework. This is done to lessen the hassle of downloading packages from `pip` using `uv` and etc. Stay tune until then!

=======
>>>>>>> 815130e (More accesible download dependencies system)
## Features

- **Chapter-Based Subdecks:** Creates a separate deck for each chapter
- **Incremental Progression:** Words learned in Chapter 1 are **skipped** in Chapter 2
- **Smart Frequency Sorting:** Words are sorted by how often they appear
- **Context Sentences:** Extracts real example sentences from the dictionary
- **Clean Anki Cards:** Includes reading (furigana), meaning, and styling

---

<<<<<<< HEAD
## Quick Start (Read This First!)
=======
## Quick Start
>>>>>>> 815130e (More accesible download dependencies system)

### Windows

1. **Double-click `setup.bat`** and follow the prompts
2. **Run the app:** Double-click `main.py` or run `python main.py` in terminal
3. **Import:** The script creates an `.apkg` file - double-click to import into Anki

### Mac / Linux

1. Open terminal in this folder
2. Run: `pip install -r requirements.txt`
3. Run: `./setup.sh` (or manually download the dictionary to `dict/` folder)
4. Run: `python main.py`

<<<<<<< HEAD
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
=======
---
>>>>>>> 815130e (More accesible download dependencies system)

## Usage

<<<<<<< HEAD
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
=======
1. Run the script: `python main.py`
2. Paste your EPUB path (drag and drop the file into terminal)
3. Choose: Include particles/grammar? (y/n)
   - `y`: Everything (desu, wa, ga, etc.)
   - `n`: Only content words (nouns, verbs, adjectives) - Recommended for vocab mining
4. The `.apkg` file is created in the same folder as your EPUB
5. Double-click to import into Anki

## Troubleshooting
>>>>>>> 815130e (More accesible download dependencies system)

**"Dictionary not found" Error**
- Did you run setup.bat/setup.sh? The dictionary file is needed in the `dict/` folder.

**"Python is not recognized" Error**
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

**Permission denied (Mac/Linux)**
- Run `chmod +x setup.sh` in terminal
