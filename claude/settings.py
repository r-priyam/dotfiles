#!/usr/bin/env python3
"""Keep the shareable part of ~/.claude/settings.json in this repo.

  claude/settings.py apply   write the repo's keys into ~/.claude/settings.json
  claude/settings.py save    copy those same keys from ~/.claude/settings.json back here

Only keys already in claude/settings.json move either way. Everything else in
~/.claude/settings.json (autoMode, remote, ...) stays on this Mac: the repo is
public. To share a new key, add it to claude/settings.json once, then `save`.
Paths into this repo are stored as {dotfiles}, so the clone can live anywhere.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOTFILES = os.path.dirname(HERE)
REPO = os.path.join(HERE, "settings.json")
LIVE = os.path.expanduser("~/.claude/settings.json")


def write(path, data, text=None):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write((text or json.dumps(data, indent=2, ensure_ascii=False)) + "\n")
    os.replace(tmp, path)  # never leave Claude Code a half-written file


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    with open(REPO) as f:
        repo = json.loads(f.read().replace("{dotfiles}", DOTFILES))
    try:
        with open(LIVE) as f:
            live = json.load(f)
    except FileNotFoundError:
        live = {}
    if cmd == "apply":
        changed = [k for k in repo if live.get(k) != repo[k]]
        os.makedirs(os.path.dirname(LIVE), exist_ok=True)
        write(LIVE, {**live, **repo})
        print(f"~/.claude/settings.json: {', '.join(changed) or 'already up to date'}")
    elif cmd == "save":
        shared = {k: live[k] for k in repo if k in live}
        write(REPO, None, json.dumps(shared, indent=2, ensure_ascii=False).replace(DOTFILES, "{dotfiles}"))
        print(f"saved {len(shared)} keys to claude/settings.json")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
