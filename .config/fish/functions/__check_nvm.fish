function __check_nvm --on-variable PWD --description 'Auto-switch node version from .nvmrc'
    if test -f .nvmrc
        nvm use 2>/dev/null
        or nvm install
    end
end
