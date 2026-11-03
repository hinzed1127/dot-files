#!/usr/bin/env python3
"""Search Hevy exercise templates (library + custom) by title words.

Use this to check whether an exercise already exists before creating a custom
one, or to find the exact title/id to use in a routine.

  find_exercise.py bench press      # every template containing both words
"""
import argparse

import hevy


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("words", nargs="+", help="words that must all appear in the title")
    ap.add_argument("--limit", type=int, default=25)
    args = ap.parse_args()

    key = hevy.load_key()
    templates = hevy.fetch_all("/exercise_templates", "exercise_templates", key, 100)
    hits = hevy.find_templates(templates, " ".join(args.words))
    for t in hits[:args.limit]:
        kind = "custom" if t["is_custom"] else "library"
        others = ",".join(t.get("secondary_muscle_groups") or []) or "-"
        print(f"{t['id']}  {t['title']}  [{t['primary_muscle_group']}; also {others}; "
              f"{t['equipment']}; {t['type']}; {kind}]")
    if not hits:
        print(f"no exercise matches: {' '.join(args.words)}")
    elif len(hits) > args.limit:
        print(f"... {len(hits) - args.limit} more; add words to narrow")


if __name__ == "__main__":
    main()
