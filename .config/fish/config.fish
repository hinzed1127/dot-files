if status is-interactive
    # Commands to run in interactive sessions can go here
end

# Homebrew - supports both Apple Silicon (/opt/homebrew) and Intel (/usr/local)
if test -x /opt/homebrew/bin/brew
    /opt/homebrew/bin/brew shellenv | source
else if test -x /usr/local/bin/brew
    /usr/local/bin/brew shellenv | source
end

# Re-prepend nvm's active node after Homebrew overwrites PATH
if set --query nvm_current_version
    fish_add_path -gm $nvm_data/$nvm_current_version/bin
end

source ~/.config/lscolors.csh # see https://github.com/trapd00r/LS_COLORS

# Default editor
set -gx EDITOR "code --wait"
set -gx VISUAL "code --wait"

# Colorized man pages via bat
set -gx MANPAGER "sh -c 'col -bx | bat -l man -p'"
set -gx MANWIDTH 999
set -gx BAT_THEME "aura-theme"

# https://blog.smittytone.net/2020/06/14/give-macos-terminal-a-better-ls/
alias ls="gls --group-directories-first  --color=auto --format=single-column -X"
alias lsa="ls -a"

alias gs="git status"
alias gd="git diff"
alias glog="git log"

function ado-items --description "List open ADO work items assigned to me"
    az boards query --wiql "SELECT [System.Id],[System.Title],[System.State],[System.WorkItemType],[System.TeamProject] FROM WorkItems WHERE [System.AssignedTo] = @me AND [System.State] <> 'Done' AND [System.State] <> 'Closed' ORDER BY [System.ChangedDate] DESC" | jq '[.[] | {id: .fields["System.Id"], project: .fields["System.TeamProject"], type: .fields["System.WorkItemType"], title: .fields["System.Title"], state: .fields["System.State"]}]'
end

function ado-open --description "Open an ADO work item in the browser by ID"
    # az boards work-item show --id $argv[1] --open  (also works but dumps JSON output)
    open "https://dev.azure.com/NJInnovation/_workitems/edit/$argv[1]"
end


# Default to dev profile in new shells; preserve explicitly switched profiles
if not set -q AWS_PROFILE
    set -gx AWS_PROFILE innov-dev
end

# alias aws-dev='aws --profile innov-dev'
# alias aws-prod='aws --profile innov-prod'

# Default to claude w/o bedrock in new shells;
if not set -q CLAUDE_CODE_USE_BEDROCK
    set -gx CLAUDE_CODE_USE_BEDROCK 0
end

# I don't know if these are still needed. Might be able to just use the `/login` command within Claude Code
alias ccwork='set -gx CLAUDE_CODE_USE_BEDROCK 1'
alias ccpersonal='set -gx CLAUDE_CODE_USE_BEDROCK 0'

alias brew-do-spencer-mode='brew update && brew upgrade && brew cleanup'
alias bdsm='brew-do-spencer-mode'

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
fish_add_path -g ~/.local/bin

# The next line updates PATH for the Google Cloud SDK.
if [ -f "$HOME/ccbox/google-cloud-sdk/path.fish.inc" ]; . "$HOME/ccbox/google-cloud-sdk/path.fish.inc"; end

# Auto-switch node version on shell startup (nvm_auto_switch handles cd via --on-variable PWD)
if status is-interactive
    nvm_auto_switch
end

# Added by Devin
fish_add_path /Users/dan.hinze@innovation.nj.gov/.codeium/windsurf/bin
