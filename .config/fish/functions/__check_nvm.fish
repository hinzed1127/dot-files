function __check_nvm --on-variable PWD --description 'Auto-switch node version from .nvmrc'
    if not test -f .nvmrc
        return
    end
    set -l nvmrc_version (cat .nvmrc)
    if test "$nvmrc_version" = "$__check_nvm_last_version"
        return
    end
    set -g __check_nvm_last_version $nvmrc_version
    nvm use 2>/dev/null
    or nvm install
end
