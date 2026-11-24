#!/usr/bin/env python3
"""Recreate herdr workspaces as Rex sessions, resuming each Claude agent.

herdr workspace -> Rex session, herdr tab -> Rex tab running
`claude --resume <id>` in the pane's cwd (drops to a shell when claude exits).

Usage:
  rex/herdr-import.py          # dry run: print the rex commands
  rex/herdr-import.py --run    # create the sessions (quit herdr first)
"""
import json
import os
import shlex
import shutil
import subprocess
import sys

HERDR = os.path.expanduser("~/.config/herdr/session.json")
REX = shutil.which("rex") or "/Applications/Rex.app/Contents/Helpers/Rex Server.rex/Contents/MacOS/rex"


def pane_command(pane):
    s = pane.get("agent_session") or {}
    if s.get("agent") == "claude" and s.get("kind") == "id":
        # Shell stays open after claude exits, like a herdr pane.
        return ["sh", "-c", f'claude --resume {shlex.quote(s["value"])}; exec "$SHELL" -l']
    return []  # plain shell


def commands(state):
    for w in state["workspaces"]:
        session = w.get("custom_name") or os.path.basename(w["identity_cwd"])
        for i, tab in enumerate(w["tabs"]):
            if list(tab["layout"]) != ["Pane"]:
                print(f"# {session}: tab {tab.get('custom_name')!r} has splits; only its focused pane is recreated", file=sys.stderr)
            pane = tab["panes"][str(tab.get("focused", tab["root_pane"]))]
            label = tab.get("custom_name") or "claude"
            cmd = pane_command(pane)
            tail = ["--", *cmd] if cmd else []
            if i == 0:
                yield [REX, "new", session, "--window", label, "-c", pane["cwd"], *tail]
            else:
                yield [REX, "window", "new", "-s", session, label, "-c", pane["cwd"], "--focus=false", *tail]


def main():
    run = "--run" in sys.argv[1:]
    if run and subprocess.run(["pgrep", "-x", "herdr"], capture_output=True).returncode == 0:
        sys.exit("herdr is still running. Quit it first so no Claude session is resumed twice.")
    with open(HERDR) as f:
        state = json.load(f)
    for cmd in commands(state):
        print(shlex.join(cmd))
        if run:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
