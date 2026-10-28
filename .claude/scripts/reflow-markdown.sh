#!/bin/sh
# Collapses markdown paragraphs (and wrapped list items) to a single line
# each, using prettier's own markdown-aware line-joining instead of a
# hand-rolled parser. --no-config bypasses any repo .prettierrc so a
# proseWrap:"preserve" override for *.md never suppresses this. A huge
# --print-width means prettier only breaks a line when the source already
# broke it across an actual paragraph/list boundary, never mid-paragraph.
#
# Invoked as a PostToolUse hook on Write|Edit; reads the hook JSON on stdin.

set -eu

file=$(node -e '
  let data = "";
  process.stdin.on("data", (c) => (data += c));
  process.stdin.on("end", () => {
    try {
      const input = JSON.parse(data);
      const f = input.tool_input && input.tool_input.file_path;
      if (f) process.stdout.write(f);
    } catch {}
  });
')

case "$file" in
  *.md) ;;
  *) exit 0 ;;
esac

[ -f "$file" ] || exit 0

# Resolve prettier's actual entry point and invoke it via `node` rather than
# executing node_modules/.bin/prettier (or npx) directly: in this harness's
# sandboxed Bash tool, exec'ing that symlink fails with a spurious
# "Permission denied" (exit 126) despite correct file permissions.
dir=$(dirname "$file")
entry=$(cd "$dir" && node -e '
  try {
    process.stdout.write(require.resolve("prettier/bin/prettier.cjs"));
  } catch {}
' 2>/dev/null)

if [ -n "$entry" ]; then
  node "$entry" --no-config --prose-wrap always --print-width 100000 --write "$file" >/dev/null 2>&1 || true
else
  cd "$dir"
  npx --yes prettier --no-config --prose-wrap always --print-width 100000 --write "$(basename "$file")" >/dev/null 2>&1 || true
fi
