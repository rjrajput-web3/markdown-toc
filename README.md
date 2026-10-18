# markdown-toc

A dependency-free Python CLI that generates a table of contents for any Markdown file — with GitHub-compatible anchor links.

## What it does

- Scans a Markdown file for `#`–`######` headings (ignores headings inside fenced code blocks)
- Generates a nested TOC with GitHub-style anchors (`#my-heading`)
- Prints the TOC to stdout, writes it to a file, or inserts/updates it **in place** between `<!-- TOC -->` and `<!-- /TOC -->` markers
- Re-running with `--in-place` updates the existing TOC instead of duplicating it

## Requirements

Python 3.8+. No dependencies — just the standard library.

## How to run

Print the TOC for a file:

```bash
python markdown_toc.py README.md
```

Write the TOC to a separate file:

```bash
python markdown_toc.py README.md -o TOC.md
```

Insert (or update) the TOC inside the file itself:

```bash
python markdown_toc.py README.md --in-place
```

Only include headings up to a given depth (e.g. `h1`–`h3`):

```bash
python markdown_toc.py README.md --in-place --max-depth 3
```

## Example

Given this input (`example.md`):

```markdown
# My Project

An example project.

## Installation

Steps here.

### From source

More steps.

## Usage

How to use it.
```

Running `python markdown_toc.py example.md` prints:

```markdown
- [My Project](#my-project)
  - [Installation](#installation)
    - [From source](#from-source)
  - [Usage](#usage)
```

With `--in-place`, that TOC is inserted right after the `# My Project` title, wrapped in `<!-- TOC -->` / `<!-- /TOC -->` markers — edit the document, re-run, and the TOC refreshes itself.

## Notes

- Anchor slugs follow GitHub's convention (lowercase, punctuation stripped, spaces become hyphens), so every link works when the file is rendered on GitHub.
- Headings inside ``` fenced code blocks are never picked up.

## License

MIT — free to use, modify, and share.
