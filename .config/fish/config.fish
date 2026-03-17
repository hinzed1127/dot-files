if status is-interactive
    # Commands to run in interactive sessions can go here
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

# Added by Windsurf
fish_add_path /Users/dan-hinze/.codeium/windsurf/bin

# Add personal bin directory to PATH
fish_add_path ~/bin

# pnpm
set --export COREPACK_ENABLE_AUTO_PIN 0

string match -q "$TERM_PROGRAM" "kiro" and . (kiro --locate-shell-integration-path fish)

# Added by `rbenv init` on Wed Feb 11 14:43:22 CST 2026
status --is-interactive; and rbenv init - --no-rehash fish | source
