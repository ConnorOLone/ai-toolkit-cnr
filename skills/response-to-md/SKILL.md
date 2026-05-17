---
name: response-to-md
description: Use when the user wants the previous assistant response copied to the clipboard as markdown. Triggers on phrases like "convert last response to markdown", "copy that as markdown", "/response-to-md".
user-invocable: true
disable-model-invocation: true
---

# Response to Markdown

Copy the **previous** assistant response (the turn immediately before this skill was invoked) to the clipboard as markdown. The bundled `extract.py` pulls the text verbatim from the session transcript — an assistant response stored there is already markdown source, so this is fully deterministic with no reformatting and no model cost.

## Steps

1. **Choose an anchor.** From the previous assistant response, pick a distinctive verbatim substring of roughly 8–15 words. It must be:
   - Copied **exactly** as written (whitespace differences are tolerated, wording is not).
   - Distinctive — avoid generic phrases that could appear elsewhere. Prefer a sentence with specific nouns, names, or numbers.
   - Taken from prose text, not from a code block or tool output.

2. **Do not repeat the anchor text in your own message** when invoking this skill. The anchor must uniquely identify the *target* response, so it should not appear in the current turn.

3. **Run the script** with the anchor as a single quoted argument:
   ```bash
   python "${CLAUDE_SKILL_DIR}/extract.py" "<anchor>"
   ```
   `${CLAUDE_SKILL_DIR}` resolves to this skill's directory whether it runs installed or from the toolkit repo. Add `--stdout` before the anchor to print the markdown instead of copying it.

4. **Report the result** — the script prints a confirmation with the character and line count. Relay it to the user.

## How it works

- The script scans `~/.claude/projects/<encoded-cwd>/*.jsonl`, finds the assistant message whose text contains the anchor, and copies that message's text blocks verbatim.
- Locating by anchor makes it **instance-safe**: when multiple Claude Code instances share one project directory (and therefore one transcript folder), the anchor still resolves to the correct session.
- On a tie, the most recent matching message wins.

## Edge cases

- **Anchor not found:** the script exits with an error. Pick a longer, more distinctive snippet and retry.
- **No clipboard tool** (Linux without `wl-copy`/`xclip`/`xsel`): re-run with `--stdout` and present the markdown in chat instead.
- **Target response is not the immediately previous turn:** the user may want an earlier response. Take the anchor from whichever response they mean — the script matches by content, not recency.
