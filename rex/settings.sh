#!/usr/bin/env bash
# Apply Rex app settings migrated from Ghostty. Rex keeps these in the app,
# not init.lua. Needs Remote Control on (Settings > General > Client Info).
# Usage: rex/settings.sh [CLIENT]   (defaults to the client this terminal runs in)
set -euo pipefail

REX="${REX_BIN_DIR:+$REX_BIN_DIR/}rex"
command -v "$REX" >/dev/null || REX="/Applications/Rex.app/Contents/Helpers/Rex Server.rex/Contents/MacOS/rex"
C=(${1:+-C "$1"})

s() { "$REX" "${C[@]}" do "client.setting.$1" "${@:2}"; }

s terminal.typography.font        value="JetBrainsMono Nerd Font"
s terminal.typography.size        value=15.5
s terminal.advanced_fonts.synthesize value=false   # font-synthetic-style = false
s terminal.advanced_fonts.smoothing  value=true    # font-thicken = true
s terminal.cursor.style           value=block
s terminal.cursor.blink           value=off
s terminal.keyboard.option        value=sends_alt  # macos-option-as-alt = true
s interface.pane_padding.horizontal value=8
s interface.pane_padding.vertical   value=8
s interface.active_panes.fade       value=surface  # dim only the background of unfocused panes; text stays readable
"$REX" "${C[@]}" do client.theme.import path="$(cd "$(dirname "$0")" && pwd)/themes/Ayu"
s themes.dark.palette             value=Ayu
s themes.light.palette            value=Ayu
s notifications.activity.system_notifications value=true
s notifications.macos.terminal_notifications  value=true
