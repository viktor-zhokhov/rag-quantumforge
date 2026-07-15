"""Заменяет термины Star Wars на вымышленные во всех документах базы знаний.

Читает исходники из knowledge_base/_raw/, применяет словарь
knowledge_base/terms_map.json и пишет анонимизированные версии
в knowledge_base/.

Замена идёт от длинных ключей к коротким и по границам слов,
чтобы полные имена заменялись раньше отдельных слов.

Запуск:
    python scripts/replace_terms.py
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "knowledge_base"
RAW_DIR = BASE / "_raw"
MAP_PATH = BASE / "terms_map.json"


def load_terms() -> dict:
    data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    return {key: value for key, value in data.items() if not key.startswith("_")}


def build_pattern(terms: dict):
    keys = sorted(terms, key=len, reverse=True)
    pattern = re.compile("|".join(r"\b" + re.escape(key) + r"\b" for key in keys))
    return pattern


def main() -> None:
    terms = load_terms()
    pattern = build_pattern(terms)
    counts = {}

    def substitute(match: re.Match) -> str:
        original = match.group(0)
        counts[original] = counts.get(original, 0) + 1
        return terms[original]

    files = sorted(RAW_DIR.glob("*.md"))
    for path in files:
        text = path.read_text(encoding="utf-8")
        replaced = pattern.sub(substitute, text)
        # Убираем фонетические транскрипции вида «(pronounced /.../)» —
        # они могут косвенно выдать исходное название.
        replaced = re.sub(r"\s*\(pronounced [^)]*\)", "", replaced)
        # Имя файла собираем из категории (префикс до "__") и вымышленного заголовка,
        # чтобы имена файлов тоже не выдавали исходную вселенную.
        category = path.name.split("__", 1)[0]
        title = replaced.splitlines()[0].lstrip("# ").strip()
        slug = re.sub(r"[^a-z0-9-]", "", title.lower().replace(" ", "-"))
        (BASE / f"{category}__{slug}.md").write_text(replaced, encoding="utf-8")

    total = sum(counts.values())
    print(f"Files processed: {len(files)}")
    print(f"Total replacements: {total}")
    top = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:15]
    for term, count in top:
        print(f"  {term} -> {terms[term]}: {count}")


if __name__ == "__main__":
    main()
