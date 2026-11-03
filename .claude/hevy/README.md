# Hevy skills: shared code

Used by the hevy-* skills in ~/.claude/skills/. Tracked with yadm.

## Setup on a new machine
1. `yadm pull`
2. Put the Hevy API key (hevy.com/settings?developer, needs Pro) in `~/.claude/hevy/.env`:
   `HEVY_API_KEY=...` (git-ignored; the dotfiles repo is public), or export `HEVY_API_KEY`.
3. `python3 -m unittest discover -s ~/.claude/hevy/tests` (needs the key; live tests are read-only).

## Layout
- `hevy.py`: API client, kg/lb conversion, request-body builders
- `analysis.py`: e1RM, trends, weekly volume by muscle
- `summary.py`, `find_exercise.py`, `add_exercise.py`, `build_routine.py`: CLIs the skills call
- `goals.md`: goals and current injuries read by the planner and check-in skills

Hevy's API has no delete endpoints, so scripts that create data default to a dry run.
