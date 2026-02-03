import hashlib
from collections import Counter, defaultdict
from os import path as osPath
from pathlib import Path
from re import compile as reCompile

import ebooklib
import fugashi
import genanki
import orjson as json
from bs4 import BeautifulSoup
from ebooklib import epub

# --- RICH IMPORTS ---
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Confirm, Prompt

# Initialize Rich Console
console = Console()
tagger = fugashi.Tagger()
jp_re = reCompile(r"[^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFFー]")
DICT_PATH = r"dict\jmdict-examples-eng-3.6.2.json"


# --- 1. DICTIONARY LOADING (Unchanged) ---
def load_dictionary():
    if not Path(DICT_PATH).exists():
        console.print(
            f"[bold red]Error:[/bold red] Dictionary not found at {DICT_PATH}"
        )
        exit()

    with console.status("[bold green]Loading JMdict..."):
        with open(DICT_PATH, mode="rb") as f:
            jmdict = json.loads(f.read())

    dict_index = defaultdict(list)
    for entry in jmdict["words"]:
        for k in entry.get("kanji", []):
            dict_index[k["text"]].append(entry)
        for r in entry.get("kana", []):
            dict_index[r["text"]].append(entry)

    console.print(f"[green]Dictionary loaded.[/green]")
    return dict_index


def get_toc_map(toc, _map=None):
    """
    Recursively flattens the TOC into a simple dictionary:
    {'filename.xhtml': 'Chapter Title'}
    """
    if _map is None:
        _map = {}

    for item in toc:
        # 1. Standard Link (The most common item)
        if isinstance(item, ebooklib.epub.Link):
            # We strip the anchor (#) to match the file name
            # e.g. "Text/chapter1.html#section1" -> "chapter1.html"
            href = item.href.split("#")[0]
            basename = osPath.basename(href)

            # Only add if not already present (keeps the first occurrence)
            if basename not in _map:
                _map[basename] = item.title

        # 2. Section/Tuple (Nested chapters)
        elif isinstance(item, tuple):
            # item is usually (SectionObject, [Child Links])
            section_node, children = item

            # Sometimes the section header itself links to a file
            if hasattr(section_node, "href"):
                href = section_node.href.split("#")[0]
                basename = osPath.basename(href)
                if basename not in _map:
                    _map[basename] = section_node.title

            # Recurse into children
            get_toc_map(children, _map)

    return _map


def get_book_data(epub_path):
    book = epub.read_epub(epub_path)
    title_meta = book.get_metadata("DC", "title")
    book_title = title_meta[0][0] if title_meta else epub_path.stem

    # 1. Build TOC Map
    toc_map = get_toc_map(book.toc)

    chapters = []

    # State Variable
    current_chapter_title = "Front Matter"

    # 2. Iterate Spine
    for item_ref in track(book.spine, description="Parsing Chapters..."):
        item = book.get_item_with_id(item_ref[0])

        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Identify file
            full_name = item.get_name()
            basename = osPath.basename(full_name)

            # Update Title State if found in TOC
            if basename in toc_map:
                current_chapter_title = toc_map[basename]

            # Extract Text
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = soup.get_text()
            clean_text = " ".join(text.split())

            # Skip empty/non-japanese files
            if len(clean_text) < 20 or not is_japanese(clean_text[:50]):
                continue

            # --- THE MERGING LOGIC ---
            # Check if we already have chapters and if the last one matches the current title
            if len(chapters) > 0 and chapters[-1]["title"] == current_chapter_title:
                # Same chapter, just a new file -> Merge text
                chapters[-1]["text"] += "\n" + clean_text
            else:
                # New chapter title -> Create new entry
                chapters.append({"title": current_chapter_title, "text": clean_text})

    return book_title, chapters


def is_japanese(text):
    return len(jp_re.sub("", text)) > 0


def extract_data(entry):
    """Returns: reading, meaning, example_html"""
    kana_list = entry.get("kana", [])
    reading = (
        kana_list[0]["text"]
        if kana_list
        else (entry.get("kanji", [])[0]["text"] if entry.get("kanji") else "Unknown")
    )

    senses = entry.get("sense", [])
    if not senses:
        return reading, "Unknown", ""

    gloss = "; ".join(g["text"] for g in senses[0].get("gloss", []))

    example_html = ""
    for sense in senses:
        if "examples" in sense:
            for ex in sense["examples"]:
                jp_sent = next(
                    (s["text"] for s in ex["sentences"] if s["lang"] == "jpn"), None
                )
                en_sent = next(
                    (s["text"] for s in ex["sentences"] if s["lang"] == "eng"), None
                )
                if jp_sent and en_sent:
                    example_html = (
                        f"{jp_sent}<br><small style='color: #666;'>{en_sent}</small>"
                    )
                    break
        if example_html:
            break

    return reading, gloss, example_html


def stable_id(s):
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)


def is_wanted_pos(node, include_particles):
    pos = node.feature.pos1
    if include_particles:
        return True
    exclude = ["助詞", "助動詞", "記号", "感動詞", "補助記号"]
    return pos not in exclude


# --- STYLES (Unchanged) ---
STYLE = """
.card { font-family: "Hiragino Kaku Gothic Pro", "Meiryo", sans-serif; font-size: 22px; text-align: center; color: #333; background-color: white; }
.nightMode .card { background-color: #2f2f31; color: #f0f0f0; }
.jp-word { font-size: 56px; font-weight: bold; margin-bottom: 10px; line-height: 1.2; }
.jp-reading { font-size: 28px; color: #555; }
.separator { border: 0; border-bottom: 2px solid #ddd; margin: 20px auto; width: 80%; }
.section-label { font-size: 14px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-top: 15px; margin-bottom: 5px; text-align: left; }
.meaning-box { text-align: left; font-size: 22px; line-height: 1.5; padding: 0 15px; }
.example-box { text-align: left; margin-top: 15px; padding: 15px; background-color: rgba(0,0,0,0.05); border-radius: 8px; font-size: 18px; line-height: 1.6; }
.freq-tag { font-size: 12px; color: #999; margin-top: 30px; font-family: monospace; }
"""

# --- MAIN LOGIC ---
if __name__ == "__main__":
    console.print(Panel.fit("[bold blue]Epub to Anki (Chapter Mode)[/bold blue]"))

    dict_index = load_dictionary()

    epub_input = Prompt.ask("\n[bold yellow]Paste .epub Book Path[/bold yellow]").strip(
        '"'
    )
    epub_path = Path(epub_input)

    if not epub_path.exists():
        console.print("[bold red]File not found![/bold red]")
        exit()

    include_particles = Confirm.ask("Include particles/grammar?", default=False)

    # 1. Get ordered chapters
    with console.status("[bold green]Reading EPUB spine...[/bold green]"):
        book_title, chapters = get_book_data(epub_path)

    console.print(f"Detected [bold]{len(chapters)}[/bold] chapters/sections.")

    # 2. Setup Anki Model (Done once)
    model = genanki.Model(
        stable_id("jp_vocab_model_v3_styled"),
        "JP Vocab (Modern)",
        fields=[
            {"name": "Word"},
            {"name": "Reading"},
            {"name": "Meaning"},
            {"name": "Frequency"},
            {"name": "Example"},
        ],
        css=STYLE,
        templates=[
            {
                "name": "Recognition",
                "qfmt": """<div class="jp-word">{{Word}}</div>""",
                "afmt": """
            <div class="jp-word">{{Word}}</div>
            <div class="jp-reading">{{Reading}}</div>
            <hr class="separator">
            <div class="section-label">Meaning</div>
            <div class="meaning-box">{{Meaning}}</div>
            {{#Example}}
                <div class="example-box"><div class="section-label" style="margin-top:0;">Context</div>{{Example}}</div>
            {{/Example}}
            <div class="freq-tag">Source: {{Frequency}}</div>
            """,
            }
        ],
    )

    # 3. Process Chapters
    global_seen_words = set()  # Stores words seen in previous chapters
    decks = []

    console.print("\n[bold cyan]Processing Chapters...[/bold cyan]")

    for i, chapter in enumerate(chapters):
        # Format: "01", "02", etc. ensures correct sorting in Anki
        chapter_num = f"{i + 1:02d}"
        chapter_name = chapter["title"]
        # print(chapter_name)
        # print(chapter.keys())

        # Create Subdeck Name: "Book Title::01_ChapterName"
        # The '::' creates the hierarchy
        deck_name = f"{book_title} Vocab::{chapter_num}_{chapter_name}"

        # Create deck
        deck = genanki.Deck(stable_id(deck_name), deck_name)

        # Tokenize this chapter
        nodes = tagger(chapter["text"])

        # Local frequency for this chapter
        chapter_lemmas = []

        for node in nodes:
            if not is_japanese(node.surface):
                continue
            if not is_wanted_pos(node, include_particles):
                continue

            lemma = node.feature.lemma
            final_word = lemma if (lemma and lemma != "*") else node.surface
            chapter_lemmas.append(final_word)

        # Count freq just for sorting this chapter's cards
        freq = Counter(chapter_lemmas)

        # Sort by frequency within chapter
        unique_words = sorted(freq.keys(), key=lambda x: -freq[x])

        notes_added = 0

        for word in unique_words:
            # IMPORTANT: Skip if we saw this word in a previous chapter
            if word in global_seen_words:
                continue

            # Mark as seen globally
            global_seen_words.add(word)

            # Create Card
            entries = dict_index.get(word, [])
            if not entries:
                continue  # Skip if no definition found

            reading, meaning, example = extract_data(entries[0])

            note = genanki.Note(
                model=model,
                fields=[
                    str(word),
                    str(reading),
                    str(meaning),
                    f"Ch.{chapter_num} (Freq: {freq[word]})",  # Source Field
                    str(example),
                ],
            )
            deck.add_note(note)
            notes_added += 1

        if notes_added > 0:
            decks.append(deck)
            console.print(
                f"  ({i + 1}) [green]✓[/green] {deck_name} ([bold]{notes_added}[/bold] new words)"
            )
        else:
            console.print(f"  [dim]- {deck_name} (No new words)[/dim]")

    # 4. Export Package
    if not decks:
        console.print("[bold red]No cards generated![/bold red]")
        exit()

    Path("exports").mkdir(exist_ok=True)
    out_path = f"{epub_path.parent}/{book_title}_Vocab.apkg"

    # Pack all subdecks into one .apkg file
    genanki.Package(decks).write_to_file(out_path)

    console.print(
        Panel(
            f"[bold green]Success![/bold green]\nSaved split deck to: {out_path}\nImport this file, and Anki will organize the folders automatically."
        )
    )
