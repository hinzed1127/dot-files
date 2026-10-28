#!/bin/bash
# Tests for notify-claude-input.sh. Run after changing the hook:
#   ~/.claude/scripts/test-notify-claude-input.sh
#
# Uses NOTIFY_DRY_RUN=1 so the hook prints the terminal-notifier arguments
# (one per line) instead of posting a banner. Prints only failures plus a
# one-line summary; exits non-zero if anything failed.

set -uo pipefail

hook="$(dirname "$0")/notify-claude-input.sh"
failures=0
passes=0

# run_hook <entrypoint> <payload-json>  -> prints dry-run output
run_hook() {
  CLAUDE_CODE_ENTRYPOINT="$1" NOTIFY_DRY_RUN=1 "$hook" <<<"$2" 2>&1
}

expect_contains() {
  local name="$1" output="$2" needle="$3"
  if grep -qxF -- "$needle" <<<"$output"; then
    passes=$((passes + 1))
  else
    failures=$((failures + 1))
    printf 'FAIL %s: expected line %q in output:\n%s\n\n' "$name" "$needle" "$output"
  fi
}

expect_empty() {
  local name="$1" output="$2"
  if [ -z "$output" ]; then
    passes=$((passes + 1))
  else
    failures=$((failures + 1))
    printf 'FAIL %s: expected no output, got:\n%s\n\n' "$name" "$output"
  fi
}

stop_payload='{"hook_event_name":"Stop","cwd":"/Users/x/code/myproj","session_id":"abc","last_assistant_message":"All 12 tests pass."}'

out=$(run_hook claude-desktop "$stop_payload")
expect_empty "desktop app sessions are left to the app's own banners" "$out"

out=$(run_hook cli "$stop_payload")
expect_contains "Stop shows the last assistant message" "$out" "stdin: All 12 tests pass."
expect_contains "title names the project" "$out" "Claude Code — myproj"
expect_contains "terminal sessions activate Ghostty on click" "$out" "com.mitchellh.ghostty"
expect_contains "banners group per session" "$out" "claude-abc"

out=$(run_hook claude-vscode "$stop_payload")
expect_contains "VS Code sessions activate VS Code on click" "$out" "com.microsoft.VSCode"

out=$(run_hook cli '{"hook_event_name":"Notification","notification_type":"permission_prompt","cwd":"/a/myproj","session_id":"abc","message":"Claude needs your permission to use Bash"}')
expect_contains "permission prompts show their message" "$out" "stdin: Claude needs your permission to use Bash"
expect_contains "permission prompts get a subtitle" "$out" "Needs your input"

out=$(run_hook cli '{"hook_event_name":"Notification","notification_type":"idle_prompt","cwd":"/a/myproj","session_id":"abc","message":"Claude is waiting for your input"}')
expect_empty "idle prompts are skipped because Stop already announced the finish" "$out"

long_message="$(printf 'line one\n\nline two %.0s' {1..40})"
out=$(run_hook cli "$(jq -nc --arg m "$long_message" '{hook_event_name:"Stop",cwd:"/a/p",session_id:"s",last_assistant_message:$m}')")
body=$(sed -n 's/^stdin: //p' <<<"$out")
if [ "$(wc -l <<<"$body")" -eq 1 ] && [ "${#body}" -le 200 ] && [[ "$body" == "line one line two"* ]] && [[ "$body" == *... ]]; then
  passes=$((passes + 1))
else
  failures=$((failures + 1))
  printf 'FAIL long messages collapse to one truncated line, got (%d chars):\n%s\n\n' "${#body}" "$body"
fi

# terminal-notifier fails to parse a -message value starting with [ ( { or a
# quote, so the message must go in on stdin, never as an argument.
out=$(run_hook cli '{"hook_event_name":"Stop","cwd":"/a/p","session_id":"s","last_assistant_message":"[x] done"}')
expect_contains "markdown-looking messages go in on stdin" "$out" "stdin: [x] done"
if grep -qxF -- "-message" <<<"$out"; then
  failures=$((failures + 1))
  printf 'FAIL message must not be passed as a -message argument:\n%s\n\n' "$out"
else
  passes=$((passes + 1))
fi

echo "notify-claude-input: $passes passed, $failures failed"
[ "$failures" -eq 0 ]
