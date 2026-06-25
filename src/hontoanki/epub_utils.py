import re
from dataclasses import dataclass
from pathlib import Path

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub
from rich.progress import track

jp_re = re.compile(r"[^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFFー]")


@dataclass
class Chapter:
    title: str
    text: str


def is_japanese(text):
    return len(jp_re.sub("", text)) > 0


def get_toc_map(toc, _map=None):
    if _map is None:
        _map = {}

    for item in toc:
        if isinstance(item, ebooklib.epub.Link):
            href = item.href.split("#")[0]
            basename = Path(href).name
            if basename not in _map:
                _map[basename] = item.title

        elif isinstance(item, tuple):
            section_node, children = item

            if hasattr(section_node, "href"):
                href = section_node.href.split("#")[0]
                basename = Path(href).name
                if basename not in _map:
                    _map[basename] = section_node.title

            get_toc_map(children, _map)

    return _map


def get_book_data(epub_path: str | Path):
    book = epub.read_epub(epub_path)
    title_meta = book.get_metadata("DC", "title")
    book_title = title_meta[0][0] if title_meta else Path(epub_path).stem

    toc_map = get_toc_map(book.toc)

    chapters: list[Chapter] = []
    current_chapter_title = "Front Matter"

    for item_ref in track(book.spine, description="Parsing Chapters..."):
        item = book.get_item_with_id(item_ref[0])

        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            full_name = item.get_name()
            basename = Path(full_name).name

            if basename in toc_map:
                current_chapter_title = toc_map[basename]

            soup = BeautifulSoup(item.get_content(), "xml")
            text = soup.get_text()
            clean_text = " ".join(text.split())

            if len(clean_text) < 20 or not is_japanese(clean_text[:50]):
                continue

            if chapters and chapters[-1].title == current_chapter_title:
                chapters[-1].text += "\n" + clean_text
            else:
                chapters.append(Chapter(title=current_chapter_title, text=clean_text))

    return book_title, chapters
