"""Execute chapter Python examples. Pseudocode must use a text fence instead.

This checks that examples run, not that their conceptual explanations are complete.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    count = 0
    for chapter in sorted((ROOT / "chapters").glob("[0-9][0-9]-*.md")):
        snippets = re.findall(r"^```python\n(.*?)^```\s*$", chapter.read_text(), flags=re.M | re.S)
        if not snippets:
            continue
        # Run a chapter's blocks together, allowing explicitly preceding definitions.
        result = subprocess.run([sys.executable, "-c", "\n\n".join(snippets)], cwd=ROOT,
                                text=True, capture_output=True, timeout=20)
        if result.returncode:
            print(chapter.name + ":\n" + result.stderr, file=sys.stderr)
            return 1
        count += len(snippets)
        print(chapter.name + ": examples ran successfully")
    print(f"Executed {count} chapter Python examples. Live integrations and pseudocode are not executed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
