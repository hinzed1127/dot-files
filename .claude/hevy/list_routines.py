#!/usr/bin/env python3
"""List Dan's Hevy routines with their ids, optionally filtered by title words.

Use this to find the ROUTINE_ID for `build_routine.py --update`. Read-only.

  list_routines.py              # every routine
  list_routines.py lower glute  # routines whose title contains both words
"""
import argparse

import hevy


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("words", nargs="*", help="words that must all appear in the title")
    args = ap.parse_args()

    key = hevy.load_key()
    routines = hevy.fetch_all("/routines", "routines", key, 10)
    if args.words:
        # find_templates only looks at "title", so it matches routines the same way.
        routines = hevy.find_templates(routines, " ".join(args.words))
    for r in routines:
        print(f"{r['id']}  {r['title']}  ({len(r['exercises'])} exercises, updated {r['updated_at'][:10]})")
    if not routines:
        print(f"no routines match: {' '.join(args.words)}")


if __name__ == "__main__":
    main()
