---
description: Start worktrees from the fetched remote default branch.
trigger: always_on
---

# Worktrees from origin, not stale local main

Create new worktrees from the fetched remote default branch, not a stale local branch. Fetch origin first, then use `git worktree add -b <branch> <path> origin/main` (substitute the actual default branch).

## Automatic synchronization

This plugin fetches origin on Cursor `workspaceOpen` and `sessionStart`, and on Devin `SessionStart`. Devin has no `workspaceOpen` equivalent. Hooks require Git and Python 3.10 or newer. They run in local IDE/CLI sessions; do not assume cloud agents execute them.

The hook follows `origin/HEAD`, falling back to an existing `origin/main` or `origin/master`. Successful fetches are cached for 45 seconds in `$XDG_STATE_HOME/personal-agent`, or `~/.local/state/personal-agent` if unset.

After fetching:
1. Fast-forward the canonical checkout's default branch only if it is already checked out and has no tracked changes. If another branch is checked out, attempt only a non-forced update of the local default-branch ref.
2. Fast-forward a linked agent worktree only if it is behind, has no unique commits, and has no tracked changes. Agent worktrees have paths under `.cursor/worktrees/`, `.windsurf/worktrees/`, or `.devin/worktrees/`, or branches beginning `cursor/`, `windsurf/`, or `devin/`.
3. Skip unsafe or unknown status. Git refuses untracked-file collisions. Failures do not block the session.

Never hard-reset, force-update a local branch, merge into a feature worktree with unique commits, or switch the canonical checkout's branch automatically. Untracked files alone do not block a safe fast-forward.

When creating a worktree, install dependencies inside that worktree using the repository's documented package manager. The synchronization hook does not install dependencies.
