#!/usr/bin/env python3
"""Save Rex sessions and bring them back after a reboot, resuming Claude chats.

  rex-sessions.py save      snapshot sessions, tabs, folders and Claude chats
  rex-sessions.py restore   recreate saved sessions that don't exist now
                  --wait    open Rex and wait for it first (used by the login agent)
  rex-sessions.py show      print the saved snapshot
  rex-sessions.py hook      Claude Code SessionStart/SessionEnd hook (reads stdin)

The hook records which Claude chat runs in which Rex pane (REX_BLOCK), then
saves a fresh snapshot, so the snapshot stays current without running save.
"""
import json
import os
import shlex
import shutil
import subprocess
import sys
import time

STATE = os.path.expanduser("~/.local/state/rex-sessions")
CHATS = os.path.join(STATE, "chats")  # one file per Rex pane: Claude session id + cwd
SNAPSHOT = os.path.join(STATE, "snapshot.json")
REX = (
    shutil.which("rex")
    or (os.environ.get("REX_BIN_DIR") and os.path.join(os.environ["REX_BIN_DIR"], "rex"))
    or "/Applications/Rex.app/Contents/Helpers/Rex Server.rex/Contents/MacOS/rex"
)


def rex(*args):
    """Run rex with --json (placed before any `--` command) and parse the result."""
    args = list(args)
    if args[0] != "do":
        cut = args.index("--") if "--" in args else len(args)
        args.insert(cut, "--json")
    out = subprocess.run([REX, *args], capture_output=True, text=True, timeout=15)
    if out.returncode:
        raise RuntimeError(f"rex {' '.join(args)}: {out.stderr.strip()}")
    return json.loads(out.stdout)


def chat_file(block):
    return os.path.join(CHATS, block.replace(":", "_") + ".json")


def save():
    snapshot, live = [], set()
    for s in rex("ls")["sessions"]:
        info = rex("window", "ls", "-s", s["session_id"])
        tabs = []
        for w in info["windows"]:
            panes = []
            for layer in w["layers"]:
                if layer["kind"] != "tiled":
                    continue  # ponytail: floating panes aren't restored
                for b in layer["blocks"]:
                    bid = b["block_id"]
                    live.add(bid)
                    try:
                        cwd = rex("do", "-b", bid, "com.superlogical.terminal.process")["foreground"]["cwd"]
                    except Exception:
                        cwd = None
                    chat = None
                    if os.path.exists(chat_file(bid)):
                        with open(chat_file(bid)) as f:
                            chat = json.load(f)
                        cwd = chat.get("cwd") or cwd
                    panes.append({"cwd": cwd, "claude_session": chat and chat["session_id"]})
            tabs.append({"label": w.get("label") or "", "panes": panes})
        snapshot.append({"label": s.get("label") or "", "tabs": tabs})
    # Drop chat records for panes that no longer exist.
    for name in os.listdir(CHATS) if os.path.isdir(CHATS) else []:
        if name[:-5].replace("_", ":", 1) not in live:
            os.remove(os.path.join(CHATS, name))
    os.makedirs(STATE, exist_ok=True)
    tmp = SNAPSHOT + ".tmp"
    with open(tmp, "w") as f:
        json.dump(snapshot, f, indent=2)
    os.replace(tmp, SNAPSHOT)  # never leave a half-written snapshot
    return snapshot


def pane_cmd(pane):
    if not pane.get("claude_session"):
        return []
    sid = shlex.quote(pane["claude_session"])
    return ["--", "sh", "-c", f'claude --resume {sid}; exec "$SHELL" -l']


def wait_for_rex(seconds=300):
    """At login: open Rex in the background and wait until its server answers."""
    subprocess.run(["open", "-ga", "Rex"])
    for _ in range(seconds // 2):
        if subprocess.run([REX, "--autostart=false", "ls"], capture_output=True).returncode == 0:
            return
        time.sleep(2)
    sys.exit("Rex server never came up; nothing restored")


def restore(dry_run=False):
    with open(SNAPSHOT) as f:
        snapshot = json.load(f)
    existing = {s.get("label") for s in rex("ls")["sessions"]}
    for s in snapshot:
        if not s["label"] or s["label"] in existing or not s["tabs"]:
            print(f"skip {s['label'] or '(unnamed)'}: already open or empty")
            continue
        for i, tab in enumerate(s["tabs"]):
            first, *rest = tab["panes"] or [{"cwd": None}]
            cwd = ["-c", first["cwd"]] if first.get("cwd") else []
            label = tab["label"] or "shell"
            if i == 0:
                cmd = ["new", s["label"], "--window", label, *cwd, *pane_cmd(first)]
            else:
                cmd = ["window", "new", "-s", s["label"], label, *cwd, "--focus=false", *pane_cmd(first)]
            print("rex " + shlex.join(cmd))
            if dry_run:
                continue
            res = rex(*cmd)
            prev = (res.get("block_ids") or res.get("initial_windows", [{}])[0].get("block_ids") or [None])[0]
            # ponytail: extra panes are re-split to the right; exact split sizes aren't kept
            for pane in rest:
                pcwd = ["-c", pane["cwd"]] if pane.get("cwd") else []
                scmd = ["split", "-s", s["label"], "-b", prev, "--split=right", "--focus=false", *pcwd, *pane_cmd(pane)]
                print("rex " + shlex.join(scmd))
                prev = rex(*scmd)["block_ids"][0]


def hook():
    event = json.load(sys.stdin)
    block = os.environ.get("REX_BLOCK")
    if not block:
        return  # not running inside Rex
    os.makedirs(CHATS, exist_ok=True)
    if event.get("hook_event_name") == "SessionEnd":
        # Forget the chat only when you quit Claude yourself (/exit, ctrl+d).
        # A reboot or closed tab also ends Claude; keep the record so restore resumes it.
        if event.get("reason") != "prompt_input_exit":
            return  # don't snapshot while things shut down: it could save a half-closed layout
        if os.path.exists(chat_file(block)):
            os.remove(chat_file(block))
    else:
        with open(chat_file(block), "w") as f:
            json.dump({"session_id": event["session_id"], "cwd": event.get("cwd")}, f)
    # Snapshot in the background so Claude Code doesn't wait on rex calls.
    subprocess.Popen([sys.executable, "-I", os.path.abspath(__file__), "save"],
                     start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "hook":
        try:
            hook()
        except Exception as e:  # a hook must never break Claude Code
            print(f"rex-sessions hook: {e}", file=sys.stderr)
    elif cmd == "save":
        snap = save()
        print(f"saved {len(snap)} sessions to {SNAPSHOT}")
    elif cmd == "restore":
        if "--wait" in sys.argv:
            wait_for_rex()
        restore(dry_run="--dry-run" in sys.argv)
    elif cmd == "show":
        with open(SNAPSHOT) as f:
            print(f.read())
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
