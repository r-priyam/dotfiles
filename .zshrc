# Fig pre block. Keep at the top of this file.
[[ -f "$HOME/.fig/shell/zshrc.pre.zsh" ]] && builtin source "$HOME/.fig/shell/zshrc.pre.zsh"

# User configuration
eval "$(/opt/homebrew/bin/brew shellenv)"

# Initialize starship
eval "$(starship init zsh)"

# Initialize pyenv if present
if [ "$(command -v pyenv)" ]; then
  eval "$(pyenv init -)"
fi

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# load docker
export PATH="$PATH:/Applications/Docker.app/Contents/Resources/bin/"
export C_INCLUDE_PATH=/opt/homebrew/Cellar/librdkafka/1.9.2/include
export LIBRARY_PATH=/opt/homebrew/Cellar/librdkafka/1.9.2/libalias python=python3.7
export PATH="/opt/homebrew/opt/llvm/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/libffi/lib"
export CPPFLAGS="-I/opt/homebrew/opt/libffi/include"

# Fig post block. Keep at the bottom of this file.
[[ -f "$HOME/.fig/shell/zshrc.post.zsh" ]] && builtin source "$HOME/.fig/shell/zshrc.post.zsh"
