#!/usr/bin/env python3
"""Show each Claude Code subagent live in its own read-only Rex pane.

  agent-panes.py hook        SubagentStart hook: open a pane next to Claude that
                             follows the subagent (reads hook JSON on stdin)
  agent-panes.py watch FILE  follow a subagent transcript; exits (closing the
                             pane) once the subagent finishes

Panes stack in a column to the right of the Claude pane. A subagent started by
another subagent opens below its parent's pane.
"""
import json
import os
import shutil
import subprocess
import sys
import time

STATE = os.path.expanduser("~/.local/state/rex-sessions/agent-panes")  # agent id -> pane
REX = (
    shutil.which("rex")
    or (os.environ.get("REX_BIN_DIR") and os.path.join(os.environ["REX_BIN_DIR"], "rex"))
    or "/Applications/Rex.app/Contents/Helpers/Rex Server.rex/Contents/MacOS/rex"
)
DIM, BOLD, RED, CYAN, OFF = "\033[2m", "\033[1m", "\033[31m", "\033[36m", "\033[0m"


def split(anchor, direction, ratio, label, transcript):
    out = subprocess.run(
        [REX, "split", "-b", anchor, f"--split={direction}", f"--ratio={ratio}", "--focus=false",
         "--label", label, "--json", "--shell=none", "--",
         sys.executable, "-I", os.path.abspath(__file__), "watch", transcript],
        capture_output=True, text=True, timeout=5)
    if out.returncode:
        return None
    return json.loads(out.stdout)["block_ids"][0]


def hook():
    event = json.load(sys.stdin)
    claude_pane = os.environ.get("REX_BLOCK")
    if not claude_pane:
        return  # not running inside Rex
    agent = event["agent_id"]
    transcript = os.path.join(event["transcript_path"][:-len(".jsonl")], "subagents", f"agent-{agent}.jsonl")
    # The agent's meta file (description, parent) is written after this hook
    # returns, so open the pane from a detached process that waits for it.
    subprocess.Popen([sys.executable, "-I", os.path.abspath(__file__), "open", claude_pane, agent, transcript],
                     start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def open_pane(claude_pane, agent, transcript):
    meta = {}
    for _ in range(50):
        try:
            with open(transcript[:-len(".jsonl")] + ".meta.json") as f:
                meta = json.load(f)
            break
        except (OSError, ValueError):
            time.sleep(0.1)
    label = f"{meta.get('agentType', 'agent')}: {meta.get('description', '')}".strip(": ")
    os.makedirs(STATE, exist_ok=True)
    last = os.path.join(STATE, claude_pane.replace(":", "_"))  # newest pane in the column
    parent = os.path.join(STATE, meta.get("parentAgentId") or "-")
    pane = None
    # Nested subagent: below its parent's pane. Otherwise: below the newest pane,
    # or, if the column is gone, a new column right of Claude.
    for anchor_file, direction, ratio in ((parent, "below", 50), (last, "below", 50)):
        if os.path.exists(anchor_file):
            with open(anchor_file) as f:
                pane = split(f.read(), direction, ratio, label, transcript)
            if pane:
                break
    pane = pane or split(claude_pane, "right", 40, label, transcript)
    if pane:
        for path in (last, os.path.join(STATE, agent)):
            with open(path, "w") as f:
                f.write(pane)


def summary(tool_input):
    for key in ("description", "command", "file_path", "url", "pattern", "query", "prompt", "path", "message"):
        if tool_input.get(key):
            return str(tool_input[key]).splitlines()[0]
    return ""


def show(entry, width):
    msg = entry.get("message") or {}
    content = msg.get("content")
    if entry.get("type") == "user" and isinstance(content, str):
        print(f"{BOLD}{content.split('<system-reminder>')[0].strip()[:600]}{OFF}\n")
    elif entry.get("type") == "assistant" and isinstance(content, list):
        for part in content:
            if part.get("type") == "text" and part["text"].strip():
                print(part["text"].strip() + "\n")
            elif part.get("type") == "tool_use":
                print(f"{CYAN}▸ {part['name']}{OFF} {DIM}{summary(part.get('input') or {})[:width - 4 - len(part['name'])]}{OFF}")
    elif entry.get("type") == "user" and isinstance(content, list):
        for part in content:
            if part.get("type") == "tool_result" and part.get("is_error"):
                print(f"  {RED}✗ failed{OFF}")


def finished(meta_path):
    try:
        with open(meta_path) as f:
            return json.load(f).get("finished")
    except (OSError, ValueError):
        return False


def watch(transcript):
    meta_path = transcript[:-len(".jsonl")] + ".meta.json"
    f, buf, idle = None, "", 0
    while True:
        if f is None and os.path.exists(transcript):
            f = open(transcript)
        chunk = f.readline() if f else ""
        if chunk:
            idle = 0
            buf += chunk
            if buf.endswith("\n"):  # skip half-written lines until they're complete
                try:
                    show(json.loads(buf), shutil.get_terminal_size().columns)
                except ValueError:
                    pass
                buf = ""
            continue
        idle += 1
        if finished(meta_path) or idle > 1800:  # ponytail: 30 min silent = Claude died
            print(f"{DIM}— done —{OFF}")
            agent = os.path.basename(transcript)[len("agent-"):-len(".jsonl")]
            if os.path.exists(os.path.join(STATE, agent)):
                os.remove(os.path.join(STATE, agent))
            time.sleep(3)  # long enough to read the last line; then the pane closes
            return
        time.sleep(1)


if __name__ == "__main__":
    if sys.argv[1:2] == ["hook"]:
        try:
            hook()
        except Exception as e:  # a hook must never break Claude Code
            print(f"agent-panes hook: {e}", file=sys.stderr)
    elif sys.argv[1:2] == ["open"] and len(sys.argv) == 5:
        open_pane(*sys.argv[2:])
    elif sys.argv[1:2] == ["watch"] and len(sys.argv) == 3:
        watch(sys.argv[2])
    else:
        sys.exit(__doc__)
