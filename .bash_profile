




#----------------------------------------#
#-https://github.com/barryclark/bashstrap-#
#-----------------------------------------#

### Aliases

# Color LS
colorflag="-G"
alias ls="command ls ${colorflag}"
alias l="ls -lF ${colorflag}" # all files, in long format
alias la="ls -laF ${colorflag}" # all files inc dotfiles, in long format
alias lsd='ls -lF ${colorflag} | grep "^d"' # only directories

# Quicker navigation
alias ..="cd .."
alias ...="cd ../.."
alias ....="cd ../../.."
alias .....="cd ../../../.."

# Enable aliases to be sudo’ed
alias sudo='sudo '

# Colored up cat!
# You must install Pygments first - "sudo easy_install Pygments"
# alias c='pygmentize -O style=monokai -f console256 -g'
alias ccat='pygmentize -O style=monokai -f console256 -g'

# Git
# You must install Git first
alias gs='git status'
alias gd='git diff'
alias gls='git log --pretty=format:"%Cgreen%h | %<(16)%Cred%an | %Cblue%ar%n%C(yellow)%s%n"'
alias ga='git add .'
alias gc='git commit -m' # requires you to type a commit message
alias gp='git push'
alias gpn='git push --set-upstream origin $(git rev-parse --abbrev-ref HEAD)'
alias gl='git pull'
alias grm='git rm $(git ls-files --deleted)'

# show commit log of unique commits of this branch (not on master)
alias diffcommitsfrommaster='git log --no-merges master..'
# show unified diff of unique commits of this branch
alias difffrommaster='git diff master...'
# ^^^^ Holy crap two dots vs three dots, so important. https://stackoverflow.com/a/48681527

# Show the diff between the latest commit and the current state
alias d='git diff-index --quiet HEAD -- || clear; git --no-pager diff --patch-with-stat'


# github cli 
alias webpr='gh pr create -w' # open a preview PR in the browser

# garbage collect old branches and detached commits
alias prune-old='git fetch --all --prune'

# Show branches, verbosely, sorted by last touch, with commit messages.
# "<" indicates you are behind, ">" indicates you are ahead, "<>" indicates you have diverged and "=" indicates that there is no difference.
alias brv="git branch --sort=-creatordate --color=always --format='%(color:reset)%(creatordate:short) %(color:bold white)%(align:2,right)%(upstream:trackshort)%(end)%(color:nobold) %(align:40,left)%(color:yellow)%(refname:short)%(end) %(color:reset)%(contents:subject)'"

# show local branches without a remote
alias brpreviewnoremote="git branch -r | awk '{print $1}' | egrep -v -f /dev/fd/0 <(git branch -vv | grep origin) | awk '{print $1}'"
# delete local branches without a remote
alias brnoremote="git branch -r | awk '{print $1}' | egrep -v -f /dev/fd/0 <(git branch -vv | grep origin) | awk '{print $1}' | xargs git branch -D"
### Prompt Colors
# Modified version of @gf3’s Sexy Bash Prompt
# (https://github.com/gf3/dotfiles)
if [[ $COLORTERM = gnome-* && $TERM = xterm ]] && infocmp gnome-256color >/dev/null 2>&1; then
	export TERM=gnome-256color
elif infocmp xterm-256color >/dev/null 2>&1; then
	export TERM=xterm-256color
fi

if tput setaf 1 &> /dev/null; then
	tput sgr0
	if [[ $(tput colors) -ge 256 ]] 2>/dev/null; then
		MAGENTA=$(tput setaf 9)
		ORANGE=$(tput setaf 172)
		GREEN=$(tput setaf 190)
		PURPLE=$(tput setaf 141)
	else
		MAGENTA=$(tput setaf 5)
		ORANGE=$(tput setaf 4)
		GREEN=$(tput setaf 2)
		PURPLE=$(tput setaf 1)
	fi
	BOLD=$(tput bold)
	RESET=$(tput sgr0)
else
	MAGENTA="\033[1;31m"
	ORANGE="\033[1;33m"
	GREEN="\033[1;32m"
	PURPLE="\033[1;35m"
	BOLD=""
	RESET="\033[m"
fi

export MAGENTA
export ORANGE
export GREEN
export PURPLE
export BOLD
export RESET

# Git branch details
function parse_git_dirty() {
	[[ $(git status 2> /dev/null | tail -n1) != *"working tree clean"* ]] && echo "*"
}

function parse_git_branch() {
	git branch --no-color 2> /dev/null | sed -e '/^[^*]/d' -e "s/* \(.*\)/\1$(parse_git_dirty)/"
}

# Change this symbol to something sweet.
# (http://en.wikipedia.org/wiki/Unicode_symbols)
symbol="⚡ "

export PS1="\[${MAGENTA}\]\u \[$RESET\]in \[$GREEN\]\w\[$RESET\]\$([[ -n \$(git branch 2> /dev/null) ]] && echo \" on \")\[$PURPLE\]\$(parse_git_branch)\[$RESET\]\n$symbol\[$RESET\]"
export PS2="\[$ORANGE\]→ \[$RESET\]"


### Misc

alias sleep-disable="sudo pmset -b sleep 0; sudo pmset -b disablesleep 1"
alias sleep-enable="sudo pmset -b sleep 5; sudo pmset -b disablesleep 0"

# Only show the current directory's name in the tab
export PROMPT_COMMAND='echo -ne "\033]0;${PWD##*/}\007"'

# init z! (https://github.com/rupa/z)
# . ~/z.sh

#-----------------------------------------#
#----------------DAN STUFF----------------#
#-----------------------------------------#
if [ -r ~/.bashrc ]; then
	source ~/.bashrc
fi

source ~/.git-completion.bash

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

export JAVA_HOME=/Library/Internet\ Plug-Ins/JavaAppletPlugin.plugin/Contents/Home

eval "$(rbenv init -)"

alias global-packages="npm ls -g --depth=0"

# Aliases related to vets.gov

alias startsocks="ssh socks -D 2001 -N &"
# check w/ 'jobs', end w/ 'fg'
# https://unix.stackexchange.com/questions/86247/what-does-ampersand-mean-at-the-end-of-a-shell-script-line
alias checksocks="curl -v --proxy socks5h://127.0.0.1:2001 sentry.vfs.va.gov"

export EXCLUDE_SIDEKIQ_ENTERPRISE="true"

alias runLocalhost="ssh -R 80:localhost:8080 ssh.localhost.run"

alias youtube="youtube-dl --extract-audio --audio-format mp3 "

touch2() { mkdir -p "$(dirname "$1")" && touch "$1" ; }

alias mongo-local="mongod --config /usr/local/etc/mongod.conf"
# alias killdocker="docker rm -f $(docker ps -a -q)"

alias bashpro="subl ~/.bash_profile"
alias bashrc="subl ~/.bashrc"

alias rbcop="bundle exec rubocop -a"

# # eval "$(starship init bash)"

function nfw() {
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --remove $(which node) ;
sudo codesign --force --sign - $(which node) ;
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add $(which node) ;
}

alias build-smoke-docker='docker build -t sso-smoketests .'
alias smoke-docker='docker container run --cap-add=SYS_ADMIN -it --rm --ipc=host --security-opt seccomp=chrome.json sso-smoketests  /bin/bash'

login_aws() {
  # get aws username
  username=$(aws sts get-caller-identity | jq -r .Arn | cut -f 2 -d'/')
  # get mfa device serial number
  serial_number=$(aws iam list-virtual-mfa-devices | jq -r --arg username "${username}" '.VirtualMFADevices[] | select(.User.UserName==$username) | .SerialNumber')
  unset AWS_SESSION_TOKEN
  # get mfa creds
  response=$(aws sts get-session-token --serial-number ${serial_number}  --token-code $1)
  export AWS_ACCESS_KEY_ID=$(echo ${response} | jq -r .Credentials.AccessKeyId)
  export AWS_SECRET_ACCESS_KEY=$(echo ${response} | jq -r .Credentials.SecretAccessKey)
  export AWS_SESSION_TOKEN=$(echo ${response} | jq -r .Credentials.SessionToken)
}

alias mfa=". issue_mfa Dan.Hinze"
# use this witht the private DNS for the day for the fwd-proxy
alias bgs="ssh -L 4447:localhost:4447"
alias kongc="lgt run kong_consumers"

function sleepgmail() {
	# Args for how many hours and minutes from now. Default to 30 min
	time=$(date -v +${1:-0}H -v +${2:-30}M +%Y-%m-%dT%H:%M:%S-6:00)
	/Applications/SelfControl.app/Contents/MacOS/selfcontrol-cli start --blocklist ~/Documents/Self\ Control/Just\ Gmail.selfcontrol --enddate $time
}

# pyenv shims and autocompletion

# add_to_path "$HOME/.cargo/bin"
# if command -v pyenv 1>/dev/null 2>&1; then
#   eval "$(pyenv init -)"
# fi

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"

pyenv-brew-relink() {
  rm -f "$HOME/.pyenv/versions/*-brew"

  for i in $(brew --cellar python)/*; do
    ln -s --force $i $HOME/.pyenv/versions/${i##/*/}-brew;
  done

  for i in $(brew --cellar python@2)/*; do
    ln -s --force $i $HOME/.pyenv/versions/${i##/*/}-brew;
  done
}

alias link-homebrew-pyenv="ln -s $(brew --cellar python)/* ~/.pyenv/versions/"
export PGHOUST=/var/pgsql_socket
# IRBRC='~/.irbrc'

add_to_path "$HOME/.poetry/bin"
#add my scripts to it
add_to_path "$HOME/bin"

# https://stackoverflow.com/questions/44232009/how-to-handle-duplicates-in-my-path-variable
# remove duplicates in path before exporting
export PATH="$(perl -e 'print join(":", grep { not $seen{$_}++ } split(/:/, $ENV{PATH}))')"

source /Users/danielhinze/.config/broot/launcher/bash/br
