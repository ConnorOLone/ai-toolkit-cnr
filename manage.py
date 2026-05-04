#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# ///
"""Interactive CLI manager for the AI toolkit.

Scans the toolkit for available assets (skills, agents, rules, hooks, configs),
shows which are currently installed on this device, and lets you toggle them
on or off with an interactive checklist.

Usage:
    aitk                       # interactive toggle UI
    aitk new <type> <name>     # scaffold a new asset
    aitk status                # show sync & drift status
    aitk --install-cli         # install the 'aitk' global command
    aitk --uninstall-cli       # remove the 'aitk' global command
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

# ── Platform-specific key reading ──────────────────────────────────────────

if platform.system() == "Windows":
    import msvcrt

    def read_key():
        key = msvcrt.getwch()
        if key in ("\x00", "\xe0"):
            key2 = msvcrt.getwch()
            return {"H": "up", "P": "down"}.get(key2, "")
        return {"\r": "enter", " ": "space", "q": "q", "\x1b": "q"}.get(key, "")
else:
    import tty
    import termios

    def read_key():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                seq = sys.stdin.read(2)
                return {"[A": "up", "[B": "down"}.get(seq, "q")
            return {"\r": "enter", "\n": "enter", " ": "space",
                    "q": "q", "\x03": "q"}.get(ch, "")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

# ── ANSI helpers ───────────────────────────────────────────────────────────

BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RED = "\033[31m"
RESET = "\033[0m"
CLEAR_SCREEN = "\033[2J\033[H"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"


def move_to(row, col=1):
    return f"\033[{row};{col}H"

# ── Asset discovery ────────────────────────────────────────────────────────

REPO_DIR = Path(__file__).resolve().parent
CLAUDE_DIR = Path.home() / ".claude"
IS_WINDOWS = platform.system() == "Windows"


class Asset:
    def __init__(self, name, category, source_path, dest_path, description=""):
        self.name = name
        self.category = category
        self.source_path = source_path
        self.dest_path = dest_path
        self.description = description
        self.installed = self._check_installed()
        self.selected = self.installed

    def _check_installed(self):
        if not self.dest_path.exists():
            return False
        if self.dest_path.is_symlink():
            return self.dest_path.resolve() == self.source_path.resolve()
        return self.dest_path.exists()

    def install(self):
        self.dest_path.parent.mkdir(parents=True, exist_ok=True)
        if self.source_path.is_dir():
            if IS_WINDOWS:
                if self.dest_path.exists():
                    shutil.rmtree(self.dest_path)
                shutil.copytree(self.source_path, self.dest_path)
            else:
                if self.dest_path.is_symlink() or self.dest_path.exists():
                    self.dest_path.unlink()
                self.dest_path.symlink_to(self.source_path)
        else:
            if IS_WINDOWS:
                shutil.copy2(self.source_path, self.dest_path)
            else:
                if self.dest_path.is_symlink() or self.dest_path.exists():
                    self.dest_path.unlink()
                self.dest_path.symlink_to(self.source_path)
        self.installed = True

    def uninstall(self):
        if not self.dest_path.exists() and not self.dest_path.is_symlink():
            self.installed = False
            return
        if self.dest_path.is_dir() and not self.dest_path.is_symlink():
            shutil.rmtree(self.dest_path)
        else:
            self.dest_path.unlink()
        self.installed = False


def parse_frontmatter(filepath):
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    meta = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip()
    return meta


def discover_skills():
    assets = []
    skills_dir = REPO_DIR / "skills"
    if not skills_dir.is_dir():
        return assets
    for d in sorted(skills_dir.iterdir()):
        if not d.is_dir():
            continue
        skill_md = d / "SKILL.md"
        if not skill_md.exists():
            continue
        meta = parse_frontmatter(skill_md)
        desc = meta.get("description", "")
        dest = CLAUDE_DIR / "skills" / d.name
        assets.append(Asset(d.name, "Skills", d, dest, desc))
    return assets


def discover_agents():
    assets = []
    agents_dir = REPO_DIR / "agents"
    if not agents_dir.is_dir():
        return assets
    for f in sorted(agents_dir.glob("*.md")):
        if f.name == "README.md":
            continue
        meta = parse_frontmatter(f)
        desc = meta.get("description", "")
        name = f.stem
        dest = CLAUDE_DIR / "agents" / f.name
        assets.append(Asset(name, "Agents", f, dest, desc))
    return assets


def discover_rules():
    assets = []
    rules_dir = REPO_DIR / "rules"
    if not rules_dir.is_dir():
        return assets
    for f in sorted(rules_dir.glob("*.md")):
        if f.name == "README.md":
            continue
        meta = parse_frontmatter(f)
        paths = meta.get("paths", "")
        desc = f"Paths: {paths}" if paths else "Always loaded"
        name = f.stem
        dest = CLAUDE_DIR / "rules" / f.name
        assets.append(Asset(name, "Rules", f, dest, desc))
    return assets


def discover_hooks():
    assets = []
    hooks_dir = REPO_DIR / "hooks"
    if not hooks_dir.is_dir():
        return assets
    for f in sorted(hooks_dir.glob("*.sh")):
        if f.name == "README.md":
            continue
        name = f.stem
        dest = CLAUDE_DIR / "hooks" / f.name
        assets.append(Asset(name, "Hooks", f, dest, "Shell script"))
    return assets


def discover_configs():
    assets = []
    claude_md = REPO_DIR / "configs" / "CLAUDE.md"
    if claude_md.exists():
        dest = CLAUDE_DIR / "CLAUDE.md"
        assets.append(Asset("CLAUDE.md", "Configs", claude_md, dest, "User-level Claude instructions"))
    configs_dir = REPO_DIR / "configs"
    if configs_dir.is_dir():
        for f in sorted(configs_dir.iterdir()):
            if f.name in ("README.md", "CLAUDE.md") or f.is_dir():
                continue
            if f.suffix == ".json":
                name = f.name
                dest = CLAUDE_DIR / f.name
                assets.append(Asset(name, "Configs", f, dest, "Configuration file"))
    return assets


def discover_all():
    all_assets = []
    for discover_fn in [discover_skills, discover_agents, discover_rules,
                        discover_hooks, discover_configs]:
        found = discover_fn()
        all_assets.extend(found)
    return all_assets

# ── Interactive UI ─────────────────────────────────────────────────────────

def render(assets, cursor, message=""):
    lines = []
    lines.append(f"{BOLD}AI Toolkit Manager{RESET}")
    lines.append(f"{DIM}↑/↓ navigate  ·  space toggle  ·  enter apply  ·  q quit{RESET}")
    lines.append("")

    current_category = None
    item_index = 0

    for asset in assets:
        if asset.category != current_category:
            current_category = asset.category
            lines.append(f"  {BOLD}{CYAN}{current_category}{RESET}")

        is_cursor = item_index == cursor
        prefix = f"{BOLD}▸{RESET}" if is_cursor else " "

        if asset.selected and asset.installed:
            check = f"{GREEN}■{RESET}"
            status = ""
        elif asset.selected and not asset.installed:
            check = f"{YELLOW}■{RESET}"
            status = f" {YELLOW}(will install){RESET}"
        elif not asset.selected and asset.installed:
            check = f"{RED}□{RESET}"
            status = f" {RED}(will remove){RESET}"
        else:
            check = f"{DIM}□{RESET}"
            status = ""

        name_style = BOLD if is_cursor else ""
        line = f"  {prefix} {check} {name_style}{asset.name}{RESET}{status}"
        lines.append(line)

        if is_cursor and asset.description:
            desc_truncated = asset.description[:80]
            lines.append(f"      {DIM}{desc_truncated}{RESET}")

        item_index += 1

    lines.append("")
    if message:
        lines.append(f"  {message}")
    else:
        changes = sum(1 for a in assets if a.selected != a.installed)
        if changes:
            lines.append(f"  {YELLOW}{changes} pending change(s) — press enter to apply{RESET}")
        else:
            lines.append(f"  {DIM}No changes pending{RESET}")

    sys.stdout.write(CLEAR_SCREEN + "\n".join(lines) + "\n")
    sys.stdout.flush()


def write_toolkit_path():
    path_file = CLAUDE_DIR / ".toolkit-path"
    path_file.write_text(str(REPO_DIR), encoding="utf-8")


def apply_changes(assets):
    installed = []
    removed = []
    for asset in assets:
        if asset.selected and not asset.installed:
            asset.install()
            installed.append(asset.name)
        elif not asset.selected and asset.installed:
            asset.uninstall()
            removed.append(asset.name)
    if installed or removed:
        write_toolkit_path()
    parts = []
    if installed:
        parts.append(f"{GREEN}Installed: {', '.join(installed)}{RESET}")
    if removed:
        parts.append(f"{RED}Removed: {', '.join(removed)}{RESET}")
    return "  ".join(parts) if parts else f"{DIM}Nothing to do{RESET}"


def run():
    assets = discover_all()

    if not assets:
        print("No assets found in the toolkit. Add skills, agents, rules, hooks,")
        print(f"or configs to: {REPO_DIR}")
        return

    cursor = 0
    message = ""

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    try:
        render(assets, cursor, message)
        while True:
            key = read_key()
            if key == "q":
                break
            elif key == "up":
                cursor = (cursor - 1) % len(assets)
                message = ""
            elif key == "down":
                cursor = (cursor + 1) % len(assets)
                message = ""
            elif key == "space":
                assets[cursor].selected = not assets[cursor].selected
                message = ""
            elif key == "enter":
                changes = sum(1 for a in assets if a.selected != a.installed)
                if changes:
                    message = apply_changes(assets)
                else:
                    message = f"{DIM}Nothing to do{RESET}"
            render(assets, cursor, message)
    finally:
        sys.stdout.write(SHOW_CURSOR + "\n")
        sys.stdout.flush()


# ── Scaffolding ────────────────────────────────────────────────────────────

SKILL_FIELDS = [
    ("name",                     True,  None,   "Lowercase with hyphens (e.g. my-skill)"),
    ("description",              True,  None,   "Start with 'Use when...' — triggering conditions only"),
    ("user-invocable",           False, "true",  "Can the user invoke this with /skill-name? (true/false)"),
    ("disable-model-invocation", False, "false", "Prevent auto-invocation by model? (true/false)"),
    ("allowed-tools",            False, "Read Write Edit Glob Grep Bash", "Space-separated tool names"),
    ("argument-hint",            False, "",      "Hint shown to user (e.g. '[topic]')"),
    ("model",                    False, "",      "Model override (sonnet/opus/haiku, blank for default)"),
]

AGENT_FIELDS = [
    ("name",          True,  None,    "Agent name with hyphens"),
    ("description",   True,  None,    "What this agent does"),
    ("allowed-tools", False, "Read Grep Glob", "Space-separated tool names"),
    ("model",         False, "sonnet", "Model to use (sonnet/opus/haiku)"),
]

RULE_FIELDS = [
    ("paths", False, "", "Glob patterns, comma-separated (e.g. src/**/*.ts, tests/**/*.ts)"),
]

HOOK_FIELDS = [
    ("event",   True,  None, "Hook event (PreToolUse/PostToolUse)"),
    ("matcher", False, "",   "Tool matcher pattern (e.g. Bash, Bash(git commit*))"),
]


def prompt_field(label, required, default, hint):
    suffix = f" {DIM}({hint}){RESET}"
    if default:
        prompt_str = f"  {label}{suffix}\n  [{default}]: "
    elif required:
        prompt_str = f"  {label} {RED}(required){RESET}{suffix}\n  : "
    else:
        prompt_str = f"  {label}{suffix}\n  [skip]: "

    while True:
        sys.stdout.write(prompt_str)
        sys.stdout.flush()
        value = input().strip()
        if not value:
            if default:
                return default
            if required:
                print(f"  {RED}This field is required.{RESET}")
                continue
            return ""
        return value


def scaffold_skill(name):
    skill_dir = REPO_DIR / "skills" / name
    if skill_dir.exists():
        print(f"{RED}Skill '{name}' already exists at {skill_dir}{RESET}")
        return
    print(f"\n{BOLD}New skill: {name}{RESET}\n")
    fields = {}
    for label, required, default, hint in SKILL_FIELDS:
        if label == "name":
            fields[label] = name
            continue
        fields[label] = prompt_field(label, required, default, hint)

    frontmatter_lines = ["---"]
    for label, _, _, _ in SKILL_FIELDS:
        val = fields.get(label, "")
        if val:
            frontmatter_lines.append(f"{label}: {val}")
    frontmatter_lines.append("---")

    body = "\n".join(frontmatter_lines) + "\n\n# " + name.replace("-", " ").title() + "\n\n"

    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")
    print(f"\n{GREEN}Created: {skill_dir / 'SKILL.md'}{RESET}")
    print(f"{DIM}Edit the file to add your skill instructions.{RESET}")


def scaffold_agent(name):
    agent_file = REPO_DIR / "agents" / f"{name}.md"
    if agent_file.exists():
        print(f"{RED}Agent '{name}' already exists at {agent_file}{RESET}")
        return
    print(f"\n{BOLD}New agent: {name}{RESET}\n")
    fields = {}
    for label, required, default, hint in AGENT_FIELDS:
        if label == "name":
            fields[label] = name
            continue
        fields[label] = prompt_field(label, required, default, hint)

    frontmatter_lines = ["---"]
    for label, _, _, _ in AGENT_FIELDS:
        val = fields.get(label, "")
        if val:
            frontmatter_lines.append(f"{label}: {val}")
    frontmatter_lines.append("---")

    body = "\n".join(frontmatter_lines) + "\n\nSystem prompt instructions here...\n"

    (REPO_DIR / "agents").mkdir(parents=True, exist_ok=True)
    agent_file.write_text(body, encoding="utf-8")
    print(f"\n{GREEN}Created: {agent_file}{RESET}")


def scaffold_rule(name):
    rule_file = REPO_DIR / "rules" / f"{name}.md"
    if rule_file.exists():
        print(f"{RED}Rule '{name}' already exists at {rule_file}{RESET}")
        return
    print(f"\n{BOLD}New rule: {name}{RESET}\n")
    fields = {}
    for label, required, default, hint in RULE_FIELDS:
        fields[label] = prompt_field(label, required, default, hint)

    lines = []
    paths = fields.get("paths", "")
    if paths:
        lines.append("---")
        lines.append("paths:")
        for p in [x.strip() for x in paths.split(",") if x.strip()]:
            lines.append(f'  - "{p}"')
        lines.append("---")
    lines.append("")
    lines.append("Instructions here...")
    lines.append("")

    (REPO_DIR / "rules").mkdir(parents=True, exist_ok=True)
    rule_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n{GREEN}Created: {rule_file}{RESET}")


def scaffold_hook(name):
    hook_file = REPO_DIR / "hooks" / f"{name}.sh"
    if hook_file.exists():
        print(f"{RED}Hook '{name}' already exists at {hook_file}{RESET}")
        return
    print(f"\n{BOLD}New hook: {name}{RESET}\n")
    fields = {}
    for label, required, default, hint in HOOK_FIELDS:
        fields[label] = prompt_field(label, required, default, hint)

    lines = [
        "#!/bin/bash",
        f"# Hook: {name}",
        f"# Event: {fields.get('event', 'PreToolUse')}",
        f"# Matcher: {fields.get('matcher', '')}",
        "",
        "set -euo pipefail",
        "",
        "input=$(cat)",
        "",
        "# Exit 0 to allow, exit 2 to block",
        "exit 0",
        "",
    ]

    (REPO_DIR / "hooks").mkdir(parents=True, exist_ok=True)
    hook_file.write_text("\n".join(lines), encoding="utf-8")
    hook_file.chmod(0o755)
    print(f"\n{GREEN}Created: {hook_file}{RESET}")
    print(f"{DIM}Register this hook in your settings.json to activate it.{RESET}")


SCAFFOLDERS = {
    "skill": scaffold_skill,
    "agent": scaffold_agent,
    "rule": scaffold_rule,
    "hook": scaffold_hook,
}


def cmd_new(args):
    if len(args) < 2:
        print(f"Usage: aitk new <type> <name>")
        print(f"Types: {', '.join(SCAFFOLDERS.keys())}")
        return
    asset_type, name = args[0], args[1]
    if asset_type not in SCAFFOLDERS:
        print(f"{RED}Unknown type: {asset_type}{RESET}")
        print(f"Types: {', '.join(SCAFFOLDERS.keys())}")
        return
    SCAFFOLDERS[asset_type](name)
    print(f"\n{DIM}Run 'aitk' to install it on this device.{RESET}")


# ── Status ─────────────────────────────────────────────────────────────────

def cmd_status():
    print(f"\n{BOLD}AI Toolkit Status{RESET}")
    print(f"{DIM}Repo: {REPO_DIR}{RESET}\n")

    # Git status
    git_available = (REPO_DIR / ".git").is_dir()
    if git_available:
        try:
            result = subprocess.run(
                ["git", "fetch", "--quiet", "origin"],
                cwd=REPO_DIR, capture_output=True, timeout=10
            )
        except Exception:
            pass

        try:
            local = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_DIR, capture_output=True, text=True
            ).stdout.strip()
            remote = subprocess.run(
                ["git", "rev-parse", "@{u}"],
                cwd=REPO_DIR, capture_output=True, text=True
            ).stdout.strip()

            if local == remote:
                print(f"  {GREEN}Git: up to date{RESET}")
            else:
                ahead = subprocess.run(
                    ["git", "rev-list", "--count", f"{remote}..{local}"],
                    cwd=REPO_DIR, capture_output=True, text=True
                ).stdout.strip()
                behind = subprocess.run(
                    ["git", "rev-list", "--count", f"{local}..{remote}"],
                    cwd=REPO_DIR, capture_output=True, text=True
                ).stdout.strip()
                parts = []
                if int(ahead) > 0:
                    parts.append(f"{YELLOW}{ahead} ahead{RESET}")
                if int(behind) > 0:
                    parts.append(f"{YELLOW}{behind} behind{RESET}")
                print(f"  Git: {', '.join(parts)}")
        except Exception:
            print(f"  {DIM}Git: could not determine remote status{RESET}")

        # Local changes
        try:
            diff = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=REPO_DIR, capture_output=True, text=True
            ).stdout.strip()
            if diff:
                count = len(diff.split("\n"))
                print(f"  {YELLOW}Local changes: {count} file(s) modified{RESET}")
            else:
                print(f"  {GREEN}Working tree: clean{RESET}")
        except Exception:
            pass
    else:
        print(f"  {DIM}Git: not a git repository{RESET}")

    print()

    # Asset status
    assets = discover_all()
    installed = [a for a in assets if a.installed]
    not_installed = [a for a in assets if not a.installed]

    print(f"  {BOLD}Assets: {len(assets)} available, {len(installed)} installed{RESET}\n")

    if installed:
        print(f"  {GREEN}Installed:{RESET}")
        for a in installed:
            # Check for drift on Windows (copies)
            drift = ""
            if IS_WINDOWS and a.dest_path.exists() and not a.dest_path.is_symlink():
                if a.source_path.is_file():
                    src_content = a.source_path.read_bytes()
                    dst_content = a.dest_path.read_bytes()
                    if src_content != dst_content:
                        drift = f" {YELLOW}(drifted — re-run aitk to update){RESET}"
            print(f"    {GREEN}■{RESET} [{a.category}] {a.name}{drift}")

    if not_installed:
        print(f"\n  {DIM}Not installed:{RESET}")
        for a in not_installed:
            print(f"    {DIM}□ [{a.category}] {a.name}{RESET}")

    print()


def install_cli():
    script_path = Path(__file__).resolve()
    if IS_WINDOWS:
        cmd_dir = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "Microsoft" / "WindowsApps"
        cmd_file = cmd_dir / "aitk.cmd"
        cmd_dir.mkdir(parents=True, exist_ok=True)
        cmd_file.write_text(f'@echo off\r\nuv run --script "{script_path}" %*\r\n', encoding="utf-8")
        print(f"Installed: {cmd_file}")
        print("You may need to restart your terminal.")
    else:
        bin_dir = Path.home() / ".local" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        wrapper = bin_dir / "aitk"
        wrapper.write_text(f'#!/bin/sh\nexec uv run --script "{script_path}" "$@"\n')
        wrapper.chmod(0o755)
        print(f"Installed: {wrapper}")
        if str(bin_dir) not in os.environ.get("PATH", ""):
            print(f"Add to your PATH if not already: export PATH=\"{bin_dir}:$PATH\"")


def uninstall_cli():
    if IS_WINDOWS:
        cmd_file = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "Microsoft" / "WindowsApps" / "aitk.cmd"
        if cmd_file.exists():
            cmd_file.unlink()
            print(f"Removed: {cmd_file}")
        else:
            print("aitk is not installed.")
    else:
        wrapper = Path.home() / ".local" / "bin" / "aitk"
        if wrapper.exists():
            wrapper.unlink()
            print(f"Removed: {wrapper}")
        else:
            print("aitk is not installed.")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--install-cli" in args:
        install_cli()
        sys.exit(0)
    if "--uninstall-cli" in args:
        uninstall_cli()
        sys.exit(0)

    if args and args[0] == "new":
        cmd_new(args[1:])
        sys.exit(0)
    if args and args[0] == "status":
        cmd_status()
        sys.exit(0)

    if not sys.stdin.isatty():
        print("Error: aitk requires an interactive terminal.")
        print("Run it directly: python3 manage.py")
        sys.exit(1)
    run()
