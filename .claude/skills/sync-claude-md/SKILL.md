---
name: sync-claude-md
description: Compares Dan's ~/.claude/CLAUDE.md against the upstream file it's forked from (obra/dotfiles) and reports what changed, then applies approved updates. Use this whenever Dan asks to check obra's CLAUDE.md for updates, sync/diff his CLAUDE.md against obra's, pull in obra's latest changes, or asks something like "has obra changed his CLAUDE.md" or "is my CLAUDE.md out of date." Also trigger on /sync-claude-md.
---

# Sync CLAUDE.md with obra/dotfiles

Dan's `~/.claude/CLAUDE.md` is a personalized fork of obra's: `https://raw.githubusercontent.com/obra/dotfiles/main/.claude/CLAUDE.md`

The two files diverge in two ways, and it matters which kind of divergence you're looking at:

1. **Dan's personalizations** — sections and details that exist only because they're Dan's, not obra's. These are never touched:
   - The `## Shell environment` section
   - The `## Browser Automation` section
   - The `@RTK.md` include at the end of the file
   - The name "Dan" everywhere obra's file says "Jesse" (partner name stays "Bot" in both)

2. **Shared sections** — everything else. For these, obra's content wins. If obra added a section, added or removed a bullet, or reworded something, Dan wants that same change reflected in his file (translated to "Dan," never reverted back to keep Dan's old wording just because it diverged). Don't try to preserve Dan's previous phrasing in a shared section once obra has changed that section — match obra, don't merge or split the difference.

## Steps

### 1. Fetch obra's current file

```bash
curl -s https://raw.githubusercontent.com/obra/dotfiles/main/.claude/CLAUDE.md
```

Save it somewhere in the scratchpad/temp directory and read it in full — don't rely on a cached copy from earlier in the conversation, obra's file may have changed since.

### 2. Read Dan's current file in full

Read `~/.claude/CLAUDE.md` in full, not just a diff — you need the whole thing to know which sections are Dan's personalizations versus shared content.

### 3. Compare section headings first

```bash
grep -n "^##\|^# " <obra-file>
grep -n "^##\|^# " ~/.claude/CLAUDE.md
```

This surfaces structural changes fast: sections obra added, removed, or renamed. Match this list against the "Dan's personalizations" list above — anything not on that list is a shared section and should exist in both files under the same heading, with the same content.

### 4. Compare body text within each shared section

For every shared section, compare obra's current wording against Dan's line by line. Look for actual content differences, not cosmetic ones — a reworded sentence that keeps the same instruction isn't a gap, but a dropped bullet, an added bullet, or a changed rule is. Watch for:

- Bullets obra added that Dan's file lacks
- Bullets obra removed that Dan's file still has
- Wording obra changed in a way that changes the instruction (not just phrasing)
- Whole sections obra added or removed since Dan's file was last synced

### 5. Report findings

Present a summary organized by section, in the order the sections appear in obra's file:

- **Unchanged** — sections that already match (list briefly, don't belabor)
- **Modified** — show what obra's version says now vs. what Dan's file currently says
- **Added** — sections or bullets obra has that Dan's file is missing entirely
- **Removed** — sections or bullets Dan's file has that obra has dropped

Keep this high-level and scannable — Dan doesn't need the full text of unchanged sections repeated back to him, just enough to confirm nothing there needs attention.

### 6. Wait for approval

Do not edit `~/.claude/CLAUDE.md` until Dan explicitly approves the changes. If he approves some but not all of the recommended changes, only apply the ones he approved.

### 7. Apply approved edits

Edit `~/.claude/CLAUDE.md` to match obra's content for the approved shared-section changes, substituting "Dan" for "Jesse." Preserve the file's existing formatting conventions (heading style, bullet style, blank-line spacing) and leave Dan's personalized sections untouched. Don't reorder sections unless the reordering itself is part of what obra changed.
