import argparse
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import fugashi
import genanki
import orjson
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.prompt import Confirm, Prompt

from .anki_utils import create_model, extract_data, stable_id
from .config import LANGUAGES, get_default_lang, set_default_lang
from .dictionary import load_dictionary
from .epub_utils import get_book_data, is_japanese

console = Console()
EXPORTS_DIR = Path(__file__).parent.parent.parent / "exports"


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert Japanese EPUB books to Anki flashcard decks.",
        epilog="Without arguments, runs in interactive mode.",
    )
    parser.add_argument("--epub", "-e", metavar="PATH", help="Path to .epub file (headless mode)")
    parser.add_argument("--particles", "-p", action="store_true", help="Include particles/grammar")
    parser.add_argument("--output", "-o", metavar="DIR", help="Output directory (default: ./exports)")
    parser.add_argument("--json", "-j", action="store_true", help="Also export vocabulary as JSON")
    parser.add_argument("--lang", "-l", metavar="CODE", choices=list(LANGUAGES.keys()),
                        help="Dictionary language code (one-time override)")
    parser.add_argument("--download-lang", "--dl", metavar="CODE", choices=list(LANGUAGES.keys()),
                        help="Download dictionary for a language and exit")
    parser.add_argument("--set-default-lang", metavar="CODE", choices=list(LANGUAGES.keys()),
                        help="Persist a default language for future runs")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed parsing info")
    return parser.parse_args(argv)


def pause():
    input("\nPress Enter to exit...")


def is_wanted_pos(node, include_particles):
    pos = node.feature.pos1
    if include_particles:
        return True
    exclude = ["助詞", "助動詞", "記号", "感動詞", "補助記号"]
    return pos not in exclude


def _open_in_anki(path):
    if not Confirm.ask("\nOpen in Anki?", default=True):
        return
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
        console.print("[green]Launching Anki...[/green]")
    except Exception as e:
        console.print(f"[yellow]Could not open Anki: {e}[/yellow]")


def _extract_lemmas(tagger, text, include_particles) -> list[str]:
    lemmas = []
    for node in tagger(text):
        if not is_japanese(node.surface):
            continue
        if not is_wanted_pos(node, include_particles):
            continue
        lemma = node.feature.lemma
        lemmas.append(lemma if (lemma and lemma != "*") else node.surface)
    return lemmas


def _process_chapters(tagger, chapters, model, dict_index, book_title, include_particles, lang="eng"):
    global_seen_words = set()
    decks = []
    vocab_data = []

    with Progress() as progress:
        task = progress.add_task("Processing chapters...", total=len(chapters))

        for i, chapter in enumerate(chapters):
            chapter_num = f"{i + 1:02d}"
            chapter_label = f"{chapter_num}_{chapter.title}"

            lemmas = _extract_lemmas(tagger, chapter.text, include_particles)
            freq = Counter(lemmas)
            unique_words = sorted(freq, key=lambda x: -freq[x])

            deck_name = f"{book_title} Vocab::{chapter_label}"
            deck = genanki.Deck(stable_id(deck_name), deck_name)
            notes_added = 0
            chapter_words = []

            for word in unique_words:
                if word in global_seen_words:
                    continue
                global_seen_words.add(word)

                entries = dict_index.get(word, [])
                if not entries:
                    continue

                entry = extract_data(entries[0], lang)
                chapter_words.append({
                    "word": str(word),
                    "reading": str(entry.reading),
                    "meaning": str(entry.meaning),
                    "frequency": freq[word],
                    "example": str(entry.example),
                })

                note = genanki.Note(
                    model=model,
                    fields=[
                        str(word), str(entry.reading), str(entry.meaning),
                        f"Ch.{chapter_num} (Freq: {freq[word]})",
                        str(entry.example),
                    ],
                )
                deck.add_note(note)
                notes_added += 1

            if notes_added > 0:
                decks.append(deck)

            vocab_data.append({
                "number": chapter_num,
                "title": chapter.title,
                "words": chapter_words,
            })

            progress.console.print(
                f"  ({i + 1}) [green]✓[/green] {deck_name} ([bold]{notes_added}[/bold] new words)"
                if notes_added > 0
                else f"  [dim]- {deck_name} (No new words)[/dim]"
            )
            progress.update(task, advance=1)

    return vocab_data, decks


def _export_json(path, book_title, vocab_data):
    payload = {"book": book_title, "chapters": vocab_data}
    with open(path, "wb") as f:
        f.write(orjson.dumps(payload, option=orjson.OPT_INDENT_2))
    console.print(f"[green]JSON export saved to {path}[/green]")


def _show_summary(apkg_path, vocab_data, decks, has_json):
    total_cards = sum(len(c["words"]) for c in vocab_data)
    total_chapters = len(decks)
    lines = [
        "[bold green]Success![/bold green]",
        f"Deck exported: {apkg_path}",
        f"Total cards: [bold]{total_cards}[/bold] across [bold]{total_chapters}[/bold] chapters",
    ]
    if has_json:
        lines.append(f"Vocabulary JSON: {apkg_path.with_suffix('.json')}")
    lines.append("Import the .apkg into Anki to start studying.")
    console.print(Panel("\n".join(lines)))


def main():
    args = _parse_args()
    console.print(Panel.fit("[bold blue]Epub to Anki (Chapter Mode)[/bold blue]"))

    if args.set_default_lang:
        set_default_lang(args.set_default_lang)
        lang_name = LANGUAGES[args.set_default_lang]
        console.print(f"[green]Default language set to [bold]{lang_name}[/bold] ({args.set_default_lang})[/green]")

    if args.download_lang:
        lang_name = LANGUAGES[args.download_lang]
        console.print(f"Downloading dictionary: [bold]{lang_name}[/bold] ({args.download_lang})...")
        try:
            load_dictionary(args.download_lang)
            console.print(f"[green]Dictionary downloaded: [bold]{lang_name}[/bold] ({args.download_lang})[/green]")
        except RuntimeError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            sys.exit(1)
        return

    default_lang = get_default_lang()
    lang = args.lang or default_lang

    if not args.epub:
        console.print("\n[bold yellow]Dictionary language:[/bold yellow]")
        for code, name in LANGUAGES.items():
            mark = " [bold](default)[/bold]" if code == default_lang else ""
            console.print(f"  [cyan]{code}[/cyan] - {name}{mark}")
        lang = Prompt.ask("Enter language code", default=default_lang)

    lang_name = LANGUAGES.get(lang, lang.upper())
    console.print(f"Dictionary: [bold]{lang_name}[/bold] ({lang})")

    tagger = fugashi.Tagger()

    try:
        dict_index = load_dictionary(lang)
    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        pause()
        return

    if args.epub:
        epub_path = Path(args.epub)
        if not epub_path.exists():
            console.print(f"[bold red]File not found:[/bold red] {args.epub}")
            sys.exit(1)
        include_particles = args.particles
    else:
        epub_input = Prompt.ask("\n[bold yellow]Paste .epub Book Path[/bold yellow]").strip('"')
        epub_path = Path(epub_input)
        if not epub_path.exists():
            console.print("[bold red]File not found![/bold red]")
            pause()
            return
        include_particles = Confirm.ask("Include particles/grammar?", default=False)

    with console.status("[bold green]Reading EPUB spine...[/bold green]"):
        book_title, chapters = get_book_data(epub_path)

    if args.verbose:
        console.print(f"[dim]Title: {book_title}, Chapters in TOC: {len(chapters)}[/dim]")

    if not chapters:
        console.print("[bold red]No Japanese content found in this EPUB![/bold red]")
        sys.exit(1) if args.epub else pause()
        return

    model = create_model()
    vocab_data, decks = _process_chapters(tagger, chapters, model, dict_index, book_title, include_particles, lang)

    if not decks:
        console.print("[bold red]No cards generated![/bold red]")
        sys.exit(1) if args.epub else pause()
        return

    output_dir = Path(args.output) if args.output else EXPORTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{book_title}_Vocab.apkg"

    genanki.Package(decks).write_to_file(out_path)

    if args.json:
        _export_json(out_path.with_suffix(".json"), book_title, vocab_data)

    _show_summary(out_path, vocab_data, decks, args.json)

    if args.epub:
        return
    _open_in_anki(out_path)
    pause()


if __name__ == "__main__":
    main()
