if status is-interactive
    # Commands to run in interactive sessions can go here
end

# Homebrew - supports both Apple Silicon (/opt/homebrew) and Intel (/usr/local)
if test -x /opt/homebrew/bin/brew
    /opt/homebrew/bin/brew shellenv | source
else if test -x /usr/local/bin/brew
    /usr/local/bin/brew shellenv | source
end

source ~/.config/lscolors.csh # see https://github.com/trapd00r/LS_COLORS

# https://blog.smittytone.net/2020/06/14/give-macos-terminal-a-better-ls/
alias ls="gls --group-directories-first  --color=auto --format=single-column -X"
alias lsa="ls -a"

alias gs="git status"
alias gd="git diff"
alias glog="git log"

alias aws-dev='aws --profile nav-dev'
alias aws-prod='aws --profile nav-prod'

# I don't know if these are still needed. Might be able to just use the `/login` command within Claude Code
alias ccwork='set CLAUDE_CODE_USE_BEDROCK 1'
alias ccpersonal='set CLAUDE_CODE_USE_BEDROCK 0'

# https://gist.github.com/eugenet8k/535bf3c51d1fc7c31cb8784e55d4dae4?permalink_comment_id=4763145#gistcomment-4763145
status is-interactive && __check_nvm

# bun
set --export BUN_INSTALL "$HOME/.bun"
set --export PATH $BUN_INSTALL/bin $PATH

# function aws-switch --description 'Switch AWS profiles'
#     set -gx AWS_PROFILE $argv[1]
#     bash -c 'source ./api/scripts/aws-switch.sh $1' bash $argv
# end

# Add personal bin directory to PATH (global, not universal — keeps fish_variables portable)
fish_add_path -g ~/bin

# Windsurf editor (machine-specific — only add if installed)
if test -d ~/.codeium/windsurf/bin
    fish_add_path -g ~/.codeium/windsurf/bin
end

# pnpm
set --export COREPACK_ENABLE_AUTO_PIN 0

# Added by `rbenv init` on Wed Feb 11 14:43:22 CST 2026
status --is-interactive; and rbenv init - --no-rehash fish | source

# Created by `pipx` on 2026-04-08 21:53:34
set PATH $PATH /Users/dan-hinze/.local/bin
