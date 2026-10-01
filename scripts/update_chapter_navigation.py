"""Refresh chapter tables of contents after changing section headings."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- chapter-navigation:start -->"
END = "<!-- chapter-navigation:end -->"


def update(path):
    text = path.read_text(encoding="utf-8")
    text = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n\n", "", text, flags=re.S)
    headings = re.findall(r"^## (.+)$", text, re.M)
    entries = []
    counts = {}
    for heading in headings:
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        if count:
            slug += "-" + str(count)
        entries.append(f"- [{heading}](#{slug})")
    navigation = START + "\n**In this chapter**\n\n" + "\n".join(entries) + "\n" + END + "\n\n"
    position = text.index("\n## ") + 1
    path.write_text(text[:position] + navigation + text[position:], encoding="utf-8")


if __name__ == "__main__":
    for chapter in sorted((ROOT / "chapters").glob("[0-9][0-9]-*.md")):
        update(chapter)
    print("Updated navigation in all 22 chapters.")
