import hashlib
from dataclasses import dataclass

import genanki

from .styles import STYLE


@dataclass
class WordEntry:
    reading: str
    meaning: str
    example: str


def stable_id(s):
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)


def extract_data(entry, lang: str = "eng") -> WordEntry:
    kana_list = entry.get("kana", [])
    reading = (
        kana_list[0]["text"]
        if kana_list
        else (entry.get("kanji", [])[0]["text"] if entry.get("kanji") else "Unknown")
    )

    senses = entry.get("sense", [])
    if not senses:
        return WordEntry(reading, "Unknown", "")

    gloss = "; ".join(g["text"] for g in senses[0].get("gloss", []))

    example_html = ""
    for sense in senses:
        if "examples" in sense:
            for ex in sense["examples"]:
                jp_sent = next(
                    (s["text"] for s in ex["sentences"] if s["lang"] == "jpn"), None
                )
                translated_sent = next(
                    (s["text"] for s in ex["sentences"] if s["lang"] == lang), None
                )
                if jp_sent and translated_sent:
                    example_html = (
                        f"{jp_sent}<br><small style='color: #666;'>{translated_sent}</small>"
                    )
                    break
        if example_html:
            break

    return WordEntry(reading, gloss, example_html)


def create_model():
    return genanki.Model(
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
