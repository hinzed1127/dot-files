# Fish shell completions for arc-to-notes

# Disable file completions by default
complete -c arc-to-notes -f

# Flags
complete -c arc-to-notes -l help    -s h -d 'Show help message'
complete -c arc-to-notes -l skip-analysis           -d 'Skip the automatic Claude analysis'
complete -c arc-to-notes -l only-analysis           -d 'Only run Claude analysis on existing notes file'
complete -c arc-to-notes -l space   -r              -d 'Filter to tabs from this space (repeatable)'
