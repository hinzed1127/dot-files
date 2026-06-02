function nvm_auto_switch --on-variable PWD --description "Auto-switch node version on directory change"
    if test -f .nvmrc -o -f .node-version
        nvm use 2>/dev/null; or nvm install
    end
end
