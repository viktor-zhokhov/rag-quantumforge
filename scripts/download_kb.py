"""Скачивает страницы с Wookieepedia (Star Wars fandom) и сохраняет чистый текст.

Один файл — одна сущность. Текст берётся из абзацев <p> статьи,
служебные плашки фандома отфильтровываются по стоп-фразам.

Запуск:
    python scripts/download_kb.py
"""
import json
import re
import html
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://starwars.fandom.com/api.php"
OUT_DIR = Path(__file__).resolve().parent.parent / "knowledge_base" / "_raw"
MAX_CHARS = 6000

# Стоп-фразы служебных плашек и не-энциклопедического текста
BLOCK = [
    "conflicting sources", "lucasfilm has not established", "multiple issues",
    "please help wookieepedia", "talk page", "for other uses",
    "no longer being up to date", "benefit from the addition",
    "editor discretion", "this article", "wookieepedia", "out of universe",
    "disambiguation", "content approaching", "three conflicting sources",
    "update the article", "remove this template", "please update",
]


def is_appearance_list(text: str) -> bool:
    """Отсеивает абзацы-списки названий (Appearances/Sources): много запятых
    при малом числе точек — это перечисление, а не связный текст."""
    commas = text.count(",")
    periods = text.count(".")
    return commas >= 15 and commas / (periods + 1) >= 6

# 36 сущностей по категориям: персонажи, планеты, технологии, организации, события, расы
ENTITIES = {
    "characters": [
        "Luke Skywalker", "Leia Organa", "Han Solo", "Darth Vader",
        "Obi-Wan Kenobi", "Yoda", "Palpatine", "Chewbacca",
        "Anakin Skywalker", "Padme Amidala", "Boba Fett", "Lando Calrissian",
    ],
    "planets": [
        "Tatooine", "Coruscant", "Hoth", "Endor", "Naboo", "Dagobah",
    ],
    "technologies": [
        "Lightsaber", "Death Star", "Millennium Falcon",
        "T-65B X-wing starfighter", "TIE/ln space superiority starfighter",
        "Blaster",
    ],
    "organizations": [
        "Galactic Empire", "Alliance to Restore the Republic", "Jedi Order",
        "Sith", "Galactic Republic",
    ],
    "events": [
        "Galactic Civil War", "Clone Wars", "Battle of Yavin",
    ],
    "species": [
        "Wookiee", "Ewok", "Hutt", "Jawa",
    ],
}


def fetch_clean(title: str) -> str:
    params = {
        "action": "parse", "page": title, "prop": "text",
        "format": "json", "redirects": "1",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={
        "User-Agent": "rag-quantumforge-kb-builder/1.0 (educational project)"
    })
    with urllib.request.urlopen(request, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if "parse" not in data:
        return ""
    raw = data["parse"]["text"]["*"]
    paragraphs = re.findall(r"<p>(.*?)</p>", raw, flags=re.S)
    cleaned = []
    for para in paragraphs:
        text = re.sub(r"<[^>]+>", "", para)
        text = html.unescape(text)
        text = re.sub(r"\[\d+\]", "", text).strip()
        if len(text) < 40:
            continue
        if any(bad in text.lower() for bad in BLOCK):
            continue
        if is_appearance_list(text):
            continue
        cleaned.append(text)
    result = "\n\n".join(cleaned)
    if len(result) > MAX_CHARS:
        result = result[:MAX_CHARS].rsplit("\n\n", 1)[0]
    return result


def slugify(title: str) -> str:
    slug = title.lower().replace(" ", "-")
    return re.sub(r"[^a-z0-9-]", "", slug)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for category, titles in ENTITIES.items():
        for title in titles:
            try:
                text = fetch_clean(title)
            except Exception as err:
                print(f"  FAIL {title}: {err}")
                continue
            if len(text) < 200:
                print(f"  SKIP {title}: too short ({len(text)})")
                continue
            path = OUT_DIR / f"{category}__{slugify(title)}.md"
            path.write_text(f"# {title}\n\n{text}\n", encoding="utf-8")
            total += 1
            print(f"  OK {path.name} ({len(text)} chars)")
            time.sleep(0.3)
    print(f"\nSaved {total} documents to {OUT_DIR}")


if __name__ == "__main__":
    main()
