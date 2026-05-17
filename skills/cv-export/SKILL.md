---
name: cv-export
description: Use when the user wants to export a markdown CV (or variant) to a polished, ATS-safe .docx file. Triggers on phrases like "export the CV", "build the docx", "generate CV-COL.docx", or when finishing a CV iteration cycle.
user-invocable: true
disable-model-invocation: false
---

# CV Export

Convert a markdown CV into an ATS-safe `.docx` by invoking the bundled `convert.py` script. Do not improvise with pandoc or other tools — this script defines the formatting contract.

## Steps

1. **Resolve the input path from `$ARGUMENTS`.**
   - If absolute or starts with `~`, use as-is.
   - If relative, resolve against the user's current working directory.
   - If the user gave a bare filename like `CV-COL.md`, search for it under `~/Documents/Main Vault/Careers/CV/` (their canonical CV location). Use Glob if needed.
   - Verify the file exists and ends in `.md`.

2. **Determine the output path.**
   - If a second argument is given, use that.
   - Otherwise, default to `<input-dir>/build/<input-stem>.docx` — the script handles this by default if no output is passed.

3. **Run the converter.**
   ```bash
   uv run --with python-docx python3 "${CLAUDE_PROJECT_DIR:-$HOME/CodeHub/ai-toolkit-cnr}/skills/cv-export/convert.py" "<input-path>" ["<output-path>"]
   ```
   Using `uv run --with python-docx` ensures `python-docx` is available without requiring a manual install step.
   The script auto-detects `<input-dir>/template.docx` and uses it as the base document, inheriting A4 page size, bullet numbering definitions, and all style settings. If no template is found, it falls back to a bare document with the same margins.

4. **Confirm the output** by reporting the absolute path of the generated `.docx`. Do not auto-open it — leave that to the user.

## Formatting Guarantees (baked into the script)

- Single column, no tables, no text boxes — ATS-safe.
- Standard fonts: Calibri body, Consolas for inline code.
- Real Word heading styles where they help parsing.
- Markdown mapping:
  - `# H1` → CV name (22pt, bold, accent colour)
  - `## H2` → uppercase section header with bottom border
  - `### H3` → role/employer line (bold)
  - `**bold**` / `*italic*` / `[text](url)` / `` `code` `` → inline runs
  - `- bullet` → bulleted list item
  - `---` → ignored (section headers handle separation)

## Edge Cases

- **Input missing:** report the exact path checked, suggest the canonical vault location.
- **Output dir not writable:** surface the error verbatim — don't silently fall back.
- **Markdown contains unsupported syntax** (tables, fenced code blocks, images): the script renders them as plain text; warn the user that the source markdown should stay CV-shaped.

## Notes

- The script is deterministic: same markdown in, byte-equivalent docx out. Safe to put generated `.docx` files under `build/` in `.gitignore`.
- Do not modify the markdown source as part of export. If the user asks to "fix and export", separate those into two operations.
