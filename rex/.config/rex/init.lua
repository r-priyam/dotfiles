-- Rex config, migrated from Ghostty (~/.config/ghostty/config).
-- Apply: rex config reload   Check: rex config check   Inspect: rex keymap
--
-- Already Rex defaults, so not repeated here:
--   cmd+d / cmd+shift+d split right/down, cmd+shift+enter zoom,
--   cmd+w close pane, cmd+shift+w close window,
--   cmd+left/right/backspace and alt+left/right line editing.
-- Visual settings (font, theme, cursor, padding, option key) live in the
-- app, not here: see ../../settings.sh.

-- Option+Backspace deletes the previous word (Ghostty: text:\x17).
rex.bind("alt+backspace", "pane.send_key", { key = "ctrl+w" })

-- Tabs on cmd+alt+arrows (replaces Rex default: pane focus).
rex.bind("cmd+alt+right", "client.tab.next")
rex.bind("cmd+alt+left", "client.tab.previous")

-- Pane focus on cmd+ctrl+arrows.
rex.bind("cmd+ctrl+right", "pane.focus.right")
rex.bind("cmd+ctrl+left", "pane.focus.left")
rex.bind("cmd+ctrl+up", "pane.focus.up")
rex.bind("cmd+ctrl+down", "pane.focus.down")

-- Pane resize on cmd+ctrl+alt+arrows. Ghostty used 50px; Rex amount is in its own units.
rex.bind("cmd+ctrl+alt+left", "pane.resize", { direction = "left" })
rex.bind("cmd+ctrl+alt+right", "pane.resize", { direction = "right" })
rex.bind("cmd+ctrl+alt+up", "pane.resize", { direction = "up" })
rex.bind("cmd+ctrl+alt+down", "pane.resize", { direction = "down" })

-- cmd+k clears the terminal, as in Ghostty (replaces Rex default: session picker).
-- Session picker moves to cmd+shift+k.
rex.bind("cmd+k", "com.superlogical.terminal.clear")
rex.bind("cmd+shift+k", "session.switch")
