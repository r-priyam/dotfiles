local wezterm = require("wezterm")

local config = wezterm.config_builder()

-- Font Settings
config.font_size = 14
config.command_palette_font_size = 18.0
config.line_height = 1.2
config.font = wezterm.font("DankMono Nerd Font")

-- Cursor settings
config.default_cursor_style = "BlinkingBar"
config.cursor_blink_ease_in = "Constant"
config.cursor_blink_ease_out = "Constant"
config.cursor_thickness = 2
config.cursor_blink_rate = 500

-- Window settings
config.initial_rows = 45
config.initial_cols = 180
config.window_padding = {
    left = 8,
	right = 8,
	top = 8,
	bottom = 4,
}

-- Appearance
-- config.color_scheme = "Gruvbox Dark"
-- config.color_scheme = "Catppuccino Mocha"
config.color_scheme = "Tokyo Night"
-- config.color_scheme = "One Half Dark"
-- config.color_scheme = "zenbones_dark"

-- Tab bar settings
config.window_decorations = "INTEGRATED_BUTTONS | RESIZE"
config.use_fancy_tab_bar = true
config.tab_max_width = 999999
config.hide_tab_bar_if_only_one_tab = false

-- Miscellaneous settings
config.max_fps = 240
config.prefer_egl = true
config.scrollback_lines = 200000
config.enable_scroll_bar = true

-- Key bindings
config.keys = {
  -- Text jumps with OPT | CMD on macOS
  { key = "LeftArrow",  mods = "OPT",       action = wezterm.action({ SendString = "\x1bb" }) },
  { key = "RightArrow", mods = "OPT",       action = wezterm.action({ SendString = "\x1bf" }) },
  { key = "Backspace",  mods = "OPT",       action = wezterm.action({ SendString = "\x17" }) },
  { key = "LeftArrow",  mods = "SUPER",     action = wezterm.action({ SendKey = { key = "Home" } }) },
  { key = "RightArrow", mods = "SUPER",     action = wezterm.action({ SendKey = { key = "End" } }) },
  { key = "RightArrow", mods = "SUPER",     action = wezterm.action({ SendString = "\x1bf" }) },
  { key = "Backspace",  mods = "SUPER",     action = wezterm.action({ SendString = "\x15" }) },

  -- Tab navigation
  { key = "RightArrow", mods = "CMD|OPT",   action = wezterm.action.ActivateTabRelative(1) },
  { key = "LeftArrow",  mods = "CMD|OPT",   action = wezterm.action.ActivateTabRelative(-1) },

  -- Pane navigation
  { key = "RightArrow", mods = "CMD|CTRL",  action = wezterm.action.ActivatePaneDirection("Right") },
  { key = "LeftArrow",  mods = "CMD|CTRL",  action = wezterm.action.ActivatePaneDirection("Left") },
  { key = "UpArrow",    mods = "CMD|CTRL",  action = wezterm.action.ActivatePaneDirection("Up") },
  { key = "DownArrow",  mods = "CMD|CTRL",  action = wezterm.action.ActivatePaneDirection("Down") },

  -- Split Tab actions
  { key = "RightArrow", mods = "CMD|SHIFT", action = wezterm.action { SplitHorizontal = { domain = "CurrentPaneDomain" } } },
  { key = "DownArrow",  mods = "CMD|SHIFT", action = wezterm.action { SplitVertical = { domain = "CurrentPaneDomain" } } },

  -- Misc actions
  { key = "k",          mods = "CMD",       action = wezterm.action.ActivateCommandPalette },
  { key = "c",          mods = "CMD|SHIFT", action = wezterm.action.ActivateCopyMode },
  { key = "w",          mods = "CMD",       action = wezterm.action.CloseCurrentPane({ confirm = true }) },
}

return config
