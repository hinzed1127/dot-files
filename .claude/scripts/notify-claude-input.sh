#!/bin/bash
# Claude Code Stop + Notification hook: tell Dan a session finished or needs
# input, with a banner that brings the right app forward when clicked.
#
# Reads the hook's JSON payload from stdin. Relevant fields:
#   hook_event_name        - "Stop" or "Notification"
#   last_assistant_message - (Stop) Claude's final reply, shown as the body
#   notification_type      - (Notification) "permission_prompt", "idle_prompt", ...
#   message                - (Notification) e.g. "Claude needs your permission to use Bash"
#   cwd, session_id        - project name for the title; per-session banner group
#
# Which app to activate comes from CLAUDE_CODE_ENTRYPOINT, which Claude Code
# passes to hooks: "claude-desktop" (the desktop app, which posts its own
# clickable banners, so this hook stays quiet), "claude-vscode" (VS Code
# extension), anything else is a terminal session in Ghostty.
#
# Usage (wired into settings.json under both Stop and Notification):
#   "command": "~/.claude/scripts/notify-claude-input.sh"
#
# Debug: NOTIFY_DRY_RUN=1 prints the terminal-notifier arguments instead of
# posting, e.g.
#   echo '{"hook_event_name":"Stop","cwd":"/tmp/foo","last_assistant_message":"hi"}' \
#     | CLAUDE_CODE_ENTRYPOINT=cli NOTIFY_DRY_RUN=1 ~/.claude/scripts/notify-claude-input.sh
# Tests: ~/.claude/scripts/test-notify-claude-input.sh

set -euo pipefail

max_message_chars=200

case "${CLAUDE_CODE_ENTRYPOINT:-}" in
  claude-desktop) exit 0 ;;
  claude-vscode) activate_bundle_id="com.microsoft.VSCode" ;;
  *) activate_bundle_id="com.mitchellh.ghostty" ;;
esac

payload="$(cat)"
field() { jq -r --arg f "$1" '.[$f] // empty' <<<"$payload"; }

event="$(field hook_event_name)"
cwd="$(field cwd)"
session_id="$(field session_id)"

if [ "$event" = "Stop" ]; then
  subtitle="Finished"
  message="$(field last_assistant_message)"
  [ -n "$message" ] || message="Claude is done"
else
  # Stop already announced the finish; the idle reminder that follows is noise.
  [ "$(field notification_type)" = "idle_prompt" ] && exit 0
  subtitle="Needs your input"
  message="$(field message)"
  [ -n "$message" ] || message="Claude Code needs your attention"
fi

# Collapse whitespace (markdown replies are multi-line) and truncate.
message="$(tr -s '[:space:]' ' ' <<<"$message" | sed 's/^ //; s/ $//')"
if [ "${#message}" -gt "$max_message_chars" ]; then
  message="${message:0:$((max_message_chars - 3))}..."
fi

project="${cwd##*/}"
[ -n "$project" ] && title="Claude Code — $project" || title="Claude Code"

# The message goes in on stdin: terminal-notifier fails to parse a -message
# argument that starts with [ ( { or a quote, which markdown replies often do.
args=(
  -title "$title"
  -subtitle "$subtitle"
  -group "claude-${session_id:-$project}"
  -activate "$activate_bundle_id"
  -sound default
)

if [ -n "${NOTIFY_DRY_RUN:-}" ]; then
  printf '%s\n' "${args[@]}" "stdin: $message"
else
  terminal-notifier "${args[@]}" <<<"$message" >/dev/null
fi
