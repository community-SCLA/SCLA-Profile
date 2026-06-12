#!/usr/bin/env python3
"""
Merge hook entries and safety deny rules into ~/.claude/settings.json.
Idempotent — safe to re-run. Never removes existing entries.
"""
import json
import os
import subprocess
from pathlib import Path

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
HOOKS_DIR = Path.home() / ".claude" / "hooks"
REPO_DIR = Path(__file__).parent.parent.resolve()


def detect_node() -> str:
    try:
        result = subprocess.run(["which", "node"], capture_output=True, text=True)
        return result.stdout.strip() or "node"
    except Exception:
        return "node"


def hook_cmd(script: str, use_node: bool = False, node_path: str = "node") -> str:
    path = str(HOOKS_DIR / script)
    if use_node:
        return f'\"{node_path}\" \"{path}\"'
    return path


def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        try:
            return json.loads(SETTINGS_PATH.read_text())
        except json.JSONDecodeError:
            print(f"Warning: could not parse {SETTINGS_PATH}, starting fresh")
    return {}


def merge_hooks(settings: dict, node: str) -> dict:
    hooks = settings.setdefault("hooks", {})

    def add_hook(event: str, matcher: str, command: str, timeout: int = None):
        event_hooks = hooks.setdefault(event, [])
        # Check if this command is already registered
        for entry in event_hooks:
            if entry.get("matcher") == matcher:
                for h in entry.get("hooks", []):
                    if command in h.get("command", ""):
                        return  # already present
        hook_def = {"type": "command", "command": command}
        if timeout:
            hook_def["timeout"] = timeout
        event_hooks.append({"matcher": matcher, "hooks": [hook_def]})

    # UserPromptSubmit
    add_hook("UserPromptSubmit", ".*", hook_cmd("skill-eval.sh"))

    # PreToolUse
    add_hook("PreToolUse", ".*", hook_cmd("pre-tool.sh"))

    # PostToolUse
    add_hook("PostToolUse", ".*", hook_cmd("post-tool.sh"))

    # Stop
    add_hook("Stop", ".*", hook_cmd("stop.sh"))
    add_hook("Stop", ".*", f'bash \"{HOOKS_DIR}/cleanup-worktrees.sh\"')

    # SessionStart
    add_hook("SessionStart", "*", "echo '{\"continue\": true, \"suppressOutput\": true}'")
    add_hook("SessionStart", "*", hook_cmd("context-mode-cache-heal.mjs", True, node))

    return settings


def merge_permissions(settings: dict) -> dict:
    perms = settings.setdefault("permissions", {})

    deny = perms.setdefault("deny", [])
    safety_denies = [
        "Bash(rm *)", "Bash(del *)", "Bash(rmdir *)", "Bash(rd *)",
        "Bash(unlink *)", "Bash(sudo *)",
        "Bash(git push --force *)", "Bash(git reset --hard *)", "Bash(git clean *)",
    ]
    for rule in safety_denies:
        if rule not in deny:
            deny.append(rule)

    ask = perms.setdefault("ask", [])
    if "Bash(git push *)" not in ask:
        ask.append("Bash(git push *)")

    return settings


def main():
    node = detect_node()
    settings = load_settings()
    settings = merge_hooks(settings, node)
    settings = merge_permissions(settings)
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(settings, indent=2))
    print(f"  ✅ Updated {SETTINGS_PATH}")


if __name__ == "__main__":
    main()
