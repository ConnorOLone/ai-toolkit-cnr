#!/usr/bin/env python3
"""Deterministically extract a Claude Code assistant response from the session
transcript and copy it to the clipboard as markdown.

An assistant response stored in the transcript JSONL is already markdown source
(Claude Code renders responses as CommonMark), so verbatim extraction yields
well-formatted markdown with no model involvement.

Usage:
    extract.py "<anchor>"             copy the matching response to the clipboard
    extract.py --stdout "<anchor>"    print to stdout instead of copying

<anchor> is a distinctive verbatim substring of the target response. It both
locates the correct session transcript (instance-safe when several Claude Code
instances share one project directory) and pins the exact message to extract.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def encode_cwd(path: str) -> str:
    """Mirror Claude Code's transcript-folder naming: path separators and the
    drive colon are replaced with single dashes."""
    return re.sub(r"[:\\/]+", "-", path.rstrip("\\/"))


def candidate_dirs() -> list[Path]:
    """Project transcript directories, current project first, then all others
    as a fallback so a moved/renamed cwd still resolves via the anchor."""
    root = Path.home() / ".claude" / "projects"
    if not root.is_dir():
        return []
    cwd = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    preferred = root / encode_cwd(cwd)
    dirs = [preferred] if preferred.is_dir() else []
    dirs += sorted(
        (d for d in root.iterdir() if d.is_dir() and d != preferred),
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )
    return dirs


def assistant_text(entry: dict) -> str | None:
    """Joined text blocks of an assistant message, or None if not applicable.
    Thinking and tool_use blocks are ignored."""
    msg = entry.get("message")
    if not isinstance(msg, dict) or msg.get("role") != "assistant":
        return None
    content = msg.get("content")
    if isinstance(content, str):
        return content.strip() or None
    if isinstance(content, list):
        parts = [
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        ]
        return "".join(parts).strip() or None
    return None


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def find_response(anchor: str) -> str:
    """Return the verbatim text of the most recent assistant message whose text
    contains the anchor (whitespace-insensitive). Raises SystemExit on failure."""
    needle = _norm(anchor)
    if not needle:
        sys.exit("error: anchor is empty")

    matches = []  # (timestamp, file_mtime, text)
    for d in candidate_dirs():
        for f in d.glob("*.jsonl"):
            try:
                lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            mtime = f.stat().st_mtime
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                text = assistant_text(entry)
                if text and needle in _norm(text):
                    matches.append((entry.get("timestamp", ""), mtime, text))

    if not matches:
        sys.exit(
            "error: no assistant response containing the anchor was found.\n"
            "Pick a longer, more distinctive verbatim snippet from the target "
            "response and try again."
        )
    matches.sort(key=lambda m: (m[0], m[1]))
    return matches[-1][2]


def copy_to_clipboard(text: str) -> None:
    """Copy UTF-8 text to the system clipboard using the platform's native tool."""
    plat = sys.platform
    if plat.startswith("win"):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", encoding="utf-8", delete=False
        )
        try:
            tmp.write(text)
            tmp.close()
            subprocess.run(
                [
                    "powershell", "-NoProfile", "-NonInteractive", "-Command",
                    f"Set-Clipboard -Value (Get-Content -Raw -Encoding utf8 "
                    f"-LiteralPath '{tmp.name}')",
                ],
                check=True,
            )
        finally:
            os.unlink(tmp.name)
        return

    tools = (
        [["pbcopy"]]
        if plat == "darwin"
        else [["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "-ib"]]
    )
    for tool in tools:
        try:
            subprocess.run(tool, input=text.encode("utf-8"), check=True)
            return
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    sys.exit(
        "error: no clipboard tool found. Install one of: "
        + ", ".join(t[0] for t in tools)
        + " — or re-run with --stdout."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract a Claude Code response.")
    parser.add_argument("--stdout", action="store_true", help="print instead of copy")
    parser.add_argument("anchor", help="distinctive verbatim snippet of the response")
    args = parser.parse_args()

    text = find_response(args.anchor)

    if args.stdout:
        # Write UTF-8 bytes directly so non-ASCII survives a non-UTF-8 console.
        sys.stdout.buffer.write((text + "\n").encode("utf-8"))
    else:
        copy_to_clipboard(text)
        chars = len(text)
        lines = text.count("\n") + 1
        print(f"Copied response to clipboard ({chars} chars, {lines} lines).")


if __name__ == "__main__":
    main()
