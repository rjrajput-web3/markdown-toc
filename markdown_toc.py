#!/usr/bin/env python3
"""
markdown-toc: dependency-free CLI that generates a table of contents
for a Markdown file.

Usage:
    python markdown_toc.py README.md                  # print TOC to stdout
    python markdown_toc.py README.md -o TOC.md         # write TOC to a file
    python markdown_toc.py README.md --in-place        # insert/update TOC in the file
    python markdown_toc.py README.md --max-depth 3     # only h1-h3 headings

When used with --in-place, the TOC is inserted between
<!-- TOC --> and <!-- /TOC --> markers. If the markers are missing,
they are added after the first heading (usually the document title).
Re-running updates the existing TOC instead of duplicating it.
"""

import argparse
import re
import sys

TOC_START = "<!-- TOC -->"
TOC_END = "<!-- /TOC -->"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


def github_slug(text: str) -> str:
    """GitHub-style heading anchor: lowercase, strip punctuation, spaces -> hyphens."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text


def extract_headings(lines):
    """Yield (level, text, slug) for ATX headings outside fenced code blocks."""
    in_fence = False
    fence_char = ""
    for line in lines:
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)[0]
            if not in_fence:
                in_fence = True
                fence_char = marker
            elif marker == fence_char:
                in_fence = False
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line.rstrip("\n"))
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            # Strip inline markdown noise from the visible text for the slug.
            plain = re.sub(r"[*_`~\[\]()]", "", text)
            if text:
                yield level, text, github_slug(plain)


def build_toc(headings, max_depth=6):
    toc = []
    for level, text, slug in headings:
        if level > max_depth:
            continue
        indent = "  " * (level - 1)
        toc.append(f"{indent}- [{text}](#{slug})")
    return "\n".join(toc)


def insert_in_place(lines, toc_text):
    """Insert or replace the TOC between TOC markers in the document lines."""
    out = []
    i = 0
    replaced = False
    while i < len(lines):
        if lines[i].strip() == TOC_START:
            out.append(TOC_START + "\n")
            out.append("\n" + toc_text + "\n\n" if toc_text else "\n")
            out.append(TOC_END + "\n")
            replaced = True
            i += 1
            while i < len(lines) and lines[i].strip() != TOC_END:
                i += 1
            i += 1  # skip the old TOC_END line too
        else:
            out.append(lines[i])
            i += 1

    if not replaced:
        # No markers: insert after the first heading (the document title).
        for j, line in enumerate(out):
            if HEADING_RE.match(line.rstrip("\n")):
                insert_at = j + 1
                block = ["\n", TOC_START + "\n", "\n",
                         toc_text + "\n" if toc_text else "", "\n",
                         TOC_END + "\n", "\n"]
                return out[:insert_at] + block + out[insert_at:]
        # No heading at all: prepend.
        block = [TOC_START + "\n", "\n",
                 toc_text + "\n" if toc_text else "", "\n",
                 TOC_END + "\n", "\n"]
        return block + out
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate a table of contents for a Markdown file."
    )
    parser.add_argument("file", help="Markdown file to read")
    parser.add_argument("-o", "--output", help="Write TOC to this file instead of stdout")
    parser.add_argument("--in-place", action="store_true",
                        help="Insert/update the TOC inside the input file")
    parser.add_argument("--max-depth", type=int, default=6, choices=range(1, 7),
                        help="Deepest heading level to include (default: 6)")
    args = parser.parse_args(argv)

    try:
        with open(args.file, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"Error: cannot read {args.file}: {e}", file=sys.stderr)
        return 1

    headings = list(extract_headings(lines))
    if not headings:
        print("No headings found.", file=sys.stderr)
        return 1

    toc = build_toc(headings, args.max_depth)

    if args.in_place:
        new_lines = insert_in_place(lines, toc)
        with open(args.file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"TOC updated in {args.file}")
    elif args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(toc + "\n")
        print(f"TOC written to {args.output}")
    else:
        print(toc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
