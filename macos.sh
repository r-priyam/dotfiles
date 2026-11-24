#!/bin/sh
# macos.sh: apply this Mac's system settings to a new one. Safe to re-run.
# Values were read from the current Mac with `defaults read`; only settings
# changed from the macOS default are here.
set -eu

# Keyboard and windows
defaults write NSGlobalDomain AppleShowAllExtensions -bool true
defaults write NSGlobalDomain AppleInterfaceStyleSwitchesAutomatically -bool true  # light/dark follows the time of day
defaults write NSGlobalDomain NSWindowShouldDragOnGesture -bool true               # ctrl+cmd+drag moves a window from anywhere

# Trackpad
defaults write NSGlobalDomain com.apple.swipescrolldirection -bool false  # natural scrolling off
defaults write com.apple.AppleMultitouchTrackpad Clicking -bool true      # tap to click

# Dock
defaults write com.apple.dock autohide -bool true
defaults write com.apple.dock autohide-delay -float 0
defaults write com.apple.dock autohide-time-modifier -float 0.5
defaults write com.apple.dock tilesize -int 55
defaults write com.apple.dock show-recents -bool false
defaults write com.apple.dock minimize-to-application -bool true
defaults write com.apple.dock expose-group-apps -bool true  # group Mission Control windows by app (AeroSpace)
defaults write com.apple.dock wvous-br-corner -int 1        # bottom-right hot corner off

# Finder
defaults write com.apple.finder ShowPathbar -bool true
defaults write com.apple.finder FXPreferredViewStyle -string Nlsv  # list view

# Window tiling
defaults write com.apple.WindowManager EnableTiledWindowMargins -bool false

killall Dock Finder 2>/dev/null || true
echo "macOS settings applied. Some take effect after logging out."
