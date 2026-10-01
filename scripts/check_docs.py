"""Offline local-link, structure, and source-manifest checks; no external fetching."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def prose_only(text):
    output = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            mark = match.group(1)
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence):
                fence = None
            continue
        if fence is None:
            output.append(line)
    return "\n".join(output), fence


def heading_ids(text):
    ids = set()
    counts = {}
    for title in re.findall(r"^#{1,6}\s+(.+)$", text, re.M):
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        ids.add(slug + ("-" + str(count) if count else ""))
    return ids


def check():
    errors = []
    files = sorted(ROOT.rglob("*.md"))
    files = [p for p in files if ".git" not in p.parts and "artifacts" not in p.parts]
    links = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        prose, fence = prose_only(text)
        if fence:
            errors.append(f"{path.relative_to(ROOT)}: unclosed code fence")
        if not re.search(r"^#\s", prose, re.M) and "ISSUE_TEMPLATE" not in str(path) and path.name != "PULL_REQUEST_TEMPLATE.md":
            errors.append(f"{path.relative_to(ROOT)}: missing title")
        for destination in re.findall(r"\[[^\]]*\]\(([^)]+)\)", prose):
            destination = destination.strip().split(' "', 1)[0].strip("<>")
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc:
                continue
            links += 1
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {destination}")
                continue
            if not target.exists():
                errors.append(f"{path.relative_to(ROOT)}: missing local target: {destination}")
            elif parsed.fragment and target.suffix == ".md":
                if unquote(parsed.fragment) not in heading_ids(prose_only(target.read_text())[0]):
                    errors.append(f"{path.relative_to(ROOT)}: missing anchor: {destination}")
    chapters = sorted((ROOT / "chapters").glob("[0-9][0-9]-*.md"))
    labs = sorted((ROOT / "labs").glob("[0-9][0-9]-*.md"))
    for name, collection, expected in [("chapters", chapters, 22), ("labs", labs, 12)]:
        if [int(p.name[:2]) for p in collection] != list(range(1, expected + 1)):
            errors.append(f"{name}: need consecutive numbering 1–{expected}")
        for path in collection:
            required = ["## Check your understanding"] if name == "chapters" else ["## Build", "## Deliver", "## Acceptance"]
            for marker in required:
                if marker not in path.read_text():
                    errors.append(f"{path.relative_to(ROOT)}: missing {marker}")
    try:
        manifest = json.loads((ROOT / "resources" / "sources.json").read_text())
        sha = manifest["ten_reference"]["commit"]
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            errors.append("source manifest: invalid commit")
        for source in manifest["ten_reference"]["paths"]:
            if source["url"] != "https://github.com/ten-framework/ten-framework/blob/" + sha + "/" + source["path"]:
                errors.append("source manifest: invalid pinned path URL")
        if len(manifest["videos"]) != 2 or any(v["content_status"] != "not_transcribed_or_viewed" for v in manifest["videos"]):
            errors.append("source manifest: unexpected video evidence status")
    except (ValueError, KeyError, OSError, TypeError) as error:
        errors.append("source manifest: " + str(error))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Validated {len(files)} Markdown files, {links} local links, {len(chapters)} chapters, {len(labs)} labs, and source manifest.")
    print("External link availability and live integrations are not checked.")
    return 0


if __name__ == "__main__":
    sys.exit(check())
