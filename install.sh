#!/bin/sh
# install.sh: link every config in this repo into place. Safe to re-run.
# A real file already at a target is moved to <target>.bak first.
# System settings are separate: ./macos.sh
set -eu
D=$(cd "$(dirname "$0")" && pwd)

link() {  # link REPO_PATH TARGET
  mkdir -p "$(dirname "$2")"
  if [ -e "$2" ] && [ ! -L "$2" ]; then
    mv "$2" "$2.bak"
    echo "moved old $2 to $2.bak"
  fi
  ln -sfn "$D/$1" "$2"
  echo "$2 -> $1"
}

# Claude Code. settings.json is merged, not linked: it also holds machine-only keys.
link claude/CLAUDE.md         ~/.claude/CLAUDE.md
link claude/RTK.md            ~/.claude/RTK.md
link claude/keybindings.json  ~/.claude/keybindings.json
python3 -I "$D/claude/settings.py" apply

# Git. Machine-only settings go in ~/.gitconfig.local.
link git/config  ~/.config/git/config
link git/ignore  ~/.config/git/ignore
if [ -f ~/.gitconfig ]; then
  mv ~/.gitconfig ~/.gitconfig.bak  # it would override ~/.config/git/config
  echo "moved old ~/.gitconfig to ~/.gitconfig.bak"
fi

# Terminal and prompt
link rex/init.lua            ~/.config/rex/init.lua
link rex/rexup               ~/.local/bin/rexup
link starship/starship.toml  ~/.config/starship.toml
link wezterm/wezterm.lua     ~/.config/wezterm/wezterm.lua

echo "Done. Rex app settings: rex/settings.sh   macOS settings: ./macos.sh"
