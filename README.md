# dotfiles

My macOS setup: Rex terminal, Starship prompt, Claude Code, git.

```sh
git clone https://github.com/r-priyam/dotfiles ~/Documents/Personal/dotfiles
cd ~/Documents/Personal/dotfiles
./install.sh   # link configs into place (safe to re-run)
./macos.sh     # system settings: Dock, Finder, trackpad
```

## Layout

One folder per tool. `install.sh` symlinks each file to where the tool reads
it, so editing either copy edits both.

| Folder | What | Lives at |
|---|---|---|
| `claude/` | Claude Code: instructions, keybindings, shared settings | `~/.claude/` |
| `git/` | git config and global ignore | `~/.config/git/` |
| `rex/` | Rex config, theme, live subagent panes | `~/.config/rex/` |
| `starship/` | prompt | `~/.config/starship.toml` |
| `wezterm/` | WezTerm (old terminal, kept for reference) | `~/.config/wezterm/` |

## What stays off this repo

The repo is public, so machine and work settings live in local files:

- **git:** `~/.gitconfig.local` (work email, `includeIf` rules)
- **Claude Code:** keys in `~/.claude/settings.json` that aren't in
  `claude/settings.json`, such as `autoMode`. `claude/settings.py apply`
  writes the shared keys in; `claude/settings.py save` copies them back after
  you change settings in Claude Code.

## Adding a tool

Make a folder, move the config in, add a `link` line to `install.sh`, run it.
