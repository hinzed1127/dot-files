# Hevy skills: shared code

Used by the hevy-* skills in ~/.claude/skills/. Tracked with yadm.

## Setup on a new machine

1. `brew install gnupg yadm`, then `yadm pull` (the fish config sets `GPG_TTY` for gpg's prompt).
2. `yadm decrypt` and enter the passphrase. This restores `~/.claude/hevy/.env` (the Hevy API key) and `~/.claude/hevy/goals.md`. The dotfiles repo is public, so both files are git-ignored and only exist in the repo as the encrypted `~/.local/share/yadm/archive`.
3. `python3 -m unittest discover -s ~/.claude/hevy/tests` (needs the key; live tests are read-only).

## Layout

- `hevy.py`: API client, kg/lb conversion, request-body builders
- `analysis.py`: e1RM, trends, weekly volume by muscle
- `summary.py`, `find_exercise.py`, `add_exercise.py`, `build_routine.py`: CLIs the skills call
- `goals.md`: goals and current injuries read by the planner and check-in skills

After changing `.env` or `goals.md`, run `yadm encrypt` and commit the updated archive.

Hevy's API has no delete endpoints, so scripts that create data default to a dry run.
