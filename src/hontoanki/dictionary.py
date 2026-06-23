import json
import re
import time
import zipfile
from collections import defaultdict
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen, Request

import orjson
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from .config import LANGUAGES, get_data_dir

console = Console()

GITHUB_RELEASES = "https://github.com/scriptin/jmdict-simplified/releases"
GITHUB_API = "https://api.github.com/repos/scriptin/jmdict-simplified/releases/latest"
USER_AGENT = "HonToAnki/0.2.0"
CACHE_TTL = 3600  # 1 hour


def find_dict_file(dict_dir: Path, lang: str = "eng"):
    if lang == "eng":
        pattern = "jmdict-examples-eng-*.json"
    else:
        pattern = f"jmdict-{lang}-*.json"
    matches = list(dict_dir.glob(pattern))
    return matches[0] if matches else None


def _get_latest_tag():
    cache_path = get_data_dir() / "tag_cache.json"

    if cache_path.exists():
        with open(cache_path) as f:
            cached = json.load(f)
        if time.time() - cached["timestamp"] < CACHE_TTL:
            return cached["tag"]

    req = Request(f"{GITHUB_RELEASES}/latest", headers={"User-Agent": USER_AGENT}, method="HEAD")
    with urlopen(req) as resp:
        final_url = resp.url

    m = re.search(r"/tag/([^/]+)$", final_url)
    if not m:
        raise RuntimeError(f"Could not extract tag from redirect URL: {final_url}")
    tag = m.group(1)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump({"timestamp": time.time(), "tag": tag}, f)

    return tag


def _get_asset_name(tag: str, lang: str) -> str:
    if lang == "eng":
        return f"jmdict-examples-eng-{tag}.json.zip"
    return f"jmdict-{lang}-{tag}.json.zip"


def _quote_tag(tag: str) -> str:
    return tag.replace("+", "%2B")


def _download_asset(url: str, dest_dir: Path, display_name: str):
    zip_path = dest_dir / "dict.zip"
    console.print(f"Downloading [cyan]{display_name}[/cyan]...")

    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        with Progress(
            TextColumn("[green]Downloading dictionary..."),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task("download", total=total)
            with open(zip_path, "wb") as f:
                while chunk := resp.read(8192):
                    f.write(chunk)
                    progress.update(task, advance=len(chunk))

    console.print("[green]Extracting...[/green]")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)
    zip_path.unlink()


def _find_asset_via_api(lang: str) -> str:
    console.print("[yellow]Falling back to GitHub API...[/yellow]")

    req = Request(GITHUB_API, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(req) as resp:
        release = json.loads(resp.read().decode())

    for a in release.get("assets", []):
        name = a.get("name", "")
        if lang == "eng":
            if "jmdict-examples-eng" in name and name.endswith(".zip"):
                return a["browser_download_url"]
        else:
            if f"jmdict-{lang}" in name and f"jmdict-examples-{lang}" not in name and name.endswith(".zip"):
                return a["browser_download_url"]

    raise RuntimeError(f"Could not find dictionary asset for language '{lang}' on GitHub release page.")


def download_dictionary(dict_dir: Path, lang: str = "eng"):
    console.print("[bold]Dictionary not found. Downloading...[/bold]")

    tag = _get_latest_tag()
    asset_name = _get_asset_name(tag, lang)
    download_url = f"{GITHUB_RELEASES}/download/{_quote_tag(tag)}/{asset_name}"

    req = Request(download_url, headers={"User-Agent": USER_AGENT}, method="HEAD")
    try:
        with urlopen(req):
            pass
    except HTTPError as e:
        if e.code != 404:
            raise
        download_url = _find_asset_via_api(lang)

    _download_asset(download_url, dict_dir, asset_name)

    found = find_dict_file(dict_dir, lang)
    if not found:
        raise RuntimeError(f"Extracted dictionary not found in {dict_dir}")

    console.print(f"[green]Dictionary saved to {found}[/green]")
    return found


def load_dictionary(lang: str = "eng"):
    data_dir = get_data_dir()
    dict_dir = data_dir / "dict" / lang
    dict_dir.mkdir(parents=True, exist_ok=True)

    dict_path = find_dict_file(dict_dir, lang)

    if not dict_path:
        old_dict_dir = data_dir / "dict"
        if lang == "eng":
            dict_path = find_dict_file(old_dict_dir, lang)

    if not dict_path:
        project_dict = Path(__file__).parent.parent.parent / "dict"
        dict_path = find_dict_file(project_dict, lang)

    if not dict_path:
        dict_path = download_dictionary(dict_dir, lang)

    with console.status("[bold green]Loading JMdict..."):
        with open(dict_path, "rb") as f:
            jmdict = orjson.loads(f.read())

        idx = defaultdict(list)
        words = jmdict["words"]

        for entry in words:
            kanji = entry.get("kanji")
            if kanji:
                for k in kanji:
                    idx[k["text"]].append(entry)
            kana = entry.get("kana")
            if kana:
                for r in kana:
                    idx[r["text"]].append(entry)

    lang_name = LANGUAGES.get(lang, lang.upper())
    console.print(f"[green]Dictionary loaded ({len(idx)} entries, {lang_name}).[/green]")
    return idx
