#!/usr/bin/env python3
"""Show each Claude Code subagent live in a read-only Rex pane, in an "agents" tab.

  agent-panes.py hook        SubagentStart hook: open a pane that follows the
                             subagent (reads hook JSON on stdin)
  agent-panes.py watch FILE  follow a subagent transcript; exits (closing the
                             pane) once the subagent finishes

The first subagent opens an "agents" tab beside Claude's tab, so Claude's pane
keeps its size. More subagents split that tab side by side; a subagent started
by another subagent opens below its parent's pane. Each pane reports its state
to Rex (Program Status Protocol), so the tab header shows a spinner while
agents run. The tab closes with its last pane.
"""
import base64
import fcntl
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


def rex_json(*args):
    out = subprocess.run([REX, *args], capture_output=True, text=True, timeout=5)
    return json.loads(out.stdout) if out.returncode == 0 else None


def watch_cmd(transcript):
    return ["--shell=none", "--", sys.executable, "-I", os.path.abspath(__file__), "watch", transcript]


def hook():
    event = json.load(sys.stdin)
    claude_pane, session = os.environ.get("REX_BLOCK"), os.environ.get("REX_SESSION")
    if not (claude_pane and session):
        return  # not running inside Rex
    agent = event["agent_id"]
    transcript = os.path.join(event["transcript_path"][:-len(".jsonl")], "subagents", f"agent-{agent}.jsonl")
    # The agent's meta file (description, parent) is written after this hook
    # returns, so open the pane from a detached process that waits for it.
    subprocess.Popen([sys.executable, "-I", os.path.abspath(__file__), "open", session, claude_pane, agent, transcript],
                     start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def open_pane(session, claude_pane, agent, transcript):
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
    last = os.path.join(STATE, claude_pane.replace(":", "_"))  # newest pane in this Claude's agents tab
    parent = os.path.join(STATE, meta.get("parentAgentId") or "-")
    # Parallel agents start together; one at a time, or each would open its own tab.
    with open(last + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        pane = None
        # Nested: below its parent. Otherwise right of the newest pane. If the
        # tab is gone (all its panes closed), open a new agents tab.
        for anchor_file, direction in ((parent, "below"), (last, "right")):
            if os.path.exists(anchor_file):
                with open(anchor_file) as f:
                    res = rex_json("split", "-b", f.read(), f"--split={direction}", "--focus=false",
                                   "--label", label, "--json", *watch_cmd(transcript))
                if res:
                    pane = res["block_ids"][0]
                    break
        if not pane:
            res = rex_json("window", "new", "-s", session, "agents", "--focus=false", "--json", *watch_cmd(transcript))
            if not res:
                return
            pane = res["block_ids"][0]
            subprocess.run([REX, "block", "rename", pane, label], capture_output=True, timeout=5)
        for path in (last, os.path.join(STATE, agent)):
            with open(path, "w") as f:
                f.write(pane)


def status(state, title, msg=""):
    """Tell Rex what this pane's agent is doing (OSC 7501)."""
    b64 = lambda t: base64.b64encode("".join(c for c in t if c.isprintable())[:150].encode()).decode()
    print(f"\033]7501;state={state}:app=claude-code:title={b64(title)}:msg={b64(msg)}\033\\", end="", flush=True)


def summary(tool_input):
    for key in ("description", "command", "file_path", "url", "pattern", "query", "prompt", "path", "message"):
        if tool_input.get(key):
            return str(tool_input[key]).splitlines()[0]
    return ""


def show(entry, width):
    """Print one transcript entry; return a one-line status for a tool call."""
    line = None
    msg = entry.get("message") or {}
    content = msg.get("content")
    if entry.get("type") == "user" and isinstance(content, str):
        print(f"{BOLD}{content.split('<system-reminder>')[0].strip()[:600]}{OFF}\n")
    elif entry.get("type") == "assistant" and isinstance(content, list):
        for part in content:
            if part.get("type") == "text" and part["text"].strip():
                print(part["text"].strip() + "\n")
            elif part.get("type") == "tool_use":
                line = f"{part['name']} {summary(part.get('input') or {})}"
                print(f"{CYAN}▸ {part['name']}{OFF} {DIM}{line[len(part['name']) + 1:][:width - 4 - len(part['name'])]}{OFF}")
    elif entry.get("type") == "user" and isinstance(content, list):
        for part in content:
            if part.get("type") == "tool_result" and part.get("is_error"):
                print(f"  {RED}✗ failed{OFF}")
    return line


def finished(meta_path):
    try:
        with open(meta_path) as f:
            return json.load(f).get("finished")
    except (OSError, ValueError):
        return False


def watch(transcript):
    meta_path = transcript[:-len(".jsonl")] + ".meta.json"
    f, buf, idle, title = None, "", 0, ""
    while True:
        if not title:
            try:
                with open(meta_path) as m:
                    title = json.load(m).get("description", "")
                status("working", title)
            except (OSError, ValueError):
                pass
        if f is None and os.path.exists(transcript):
            f = open(transcript)
        chunk = f.readline() if f else ""
        if chunk:
            idle = 0
            buf += chunk
            if buf.endswith("\n"):  # skip half-written lines until they're complete
                try:
                    line = show(json.loads(buf), shutil.get_terminal_size().columns)
                    if line:
                        status("working", title, line)
                except ValueError:
                    pass
                buf = ""
            continue
        idle += 1
        if finished(meta_path) or idle > 1800:  # ponytail: 30 min silent = Claude died
            print(f"{DIM}— done —{OFF}")
            status("done", title)
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
    elif sys.argv[1:2] == ["open"] and len(sys.argv) == 6:
        open_pane(*sys.argv[2:])
    elif sys.argv[1:2] == ["watch"] and len(sys.argv) == 3:
        watch(sys.argv[2])
    else:
        sys.exit(__doc__)
