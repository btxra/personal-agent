#!/usr/bin/env python3
"""Fetch origin and fast-forward local default branch + fresh Cursor worktrees.

Machine-local personal-agent hook. Fail-open: always exit 0 and print JSON.

Preferred order:
1. Fetch origin/<default> into the shared repo.
2. Fast-forward the canonical checkout's default branch when it is clean.
3. If this workspace is a fresh Cursor worktree (behind, no unique commits,
   no tracked dirty files), fast-forward it onto origin/<default>.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

FETCH_TTL_SEC = 45
LOCK_DIR = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state") / "personal-agent"


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")


def read_input() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def git(args: list[str], cwd: Path | None = None, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["GIT_PAGER"] = "cat"
    return subprocess.run(
        ["git", "-c", "advice.detachedHead=false", *args],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def git_ok(args: list[str], cwd: Path | None = None, timeout: int = 60) -> str | None:
    proc = git(args, cwd=cwd, timeout=timeout)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def has_tracked_dirty(cwd: Path) -> bool:
    proc = git(["status", "--porcelain=v1", "-uno"], cwd=cwd)
    if proc.returncode != 0:
        raise RuntimeError("cannot determine tracked working-tree status; skipping sync")
    return bool(proc.stdout.strip())


def default_branch(cwd: Path) -> str:
    head = git_ok(["symbolic-ref", "-q", "refs/remotes/origin/HEAD"], cwd=cwd)
    if head and head.startswith("refs/remotes/origin/"):
        return head.removeprefix("refs/remotes/origin/")
    for name in ("main", "master"):
        if git(["show-ref", "--verify", "--quiet", f"refs/remotes/origin/{name}"], cwd=cwd).returncode == 0:
            return name
    return "main"


def canon_path(cwd: Path) -> Path | None:
    common = git_ok(["rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=cwd)
    if not common:
        return None
    common_path = Path(common)
    if common_path.name != ".git":
        return None
    return common_path.parent


def is_linked_worktree(cwd: Path) -> bool:
    git_dir = git_ok(["rev-parse", "--path-format=absolute", "--git-dir"], cwd=cwd)
    common = git_ok(["rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=cwd)
    return bool(git_dir and common and git_dir != common)


def is_cursor_worktree(cwd: Path, branch: str) -> bool:
    parts = tuple(part.lower() for part in cwd.parts)
    managed_path = any(parts[i] in (".cursor", ".windsurf", ".devin") and parts[i + 1] == "worktrees" for i in range(len(parts) - 1))
    return managed_path or branch.startswith(("cursor/", "windsurf/", "devin/"))


def count_commits(a: str, b: str, cwd: Path) -> int:
    out = git_ok(["rev-list", "--count", f"{a}..{b}"], cwd=cwd)
    if out is None:
        raise RuntimeError("cannot determine branch divergence; skipping sync")
    return int(out)


def workspace_root(event: dict) -> Path | None:
    env_root = os.environ.get("CURSOR_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR")
    if env_root:
        return Path(env_root)
    roots = event.get("workspace_roots")
    if isinstance(roots, list) and roots and isinstance(roots[0], str):
        return Path(roots[0])
    try:
        return Path.cwd()
    except OSError:
        return None


def stamp_path_for(common_dir: str) -> Path:
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(common_dir.encode()).hexdigest()[:16]
    return LOCK_DIR / f"{digest}.fetched"


def should_skip_fetch(common_dir: str) -> bool:
    stamp = stamp_path_for(common_dir)
    try:
        age = stamp.stat().st_mtime
    except OSError:
        return False
    return (time.time() - age) < FETCH_TTL_SEC


def mark_fetched(common_dir: str) -> None:
    stamp_path_for(common_dir).write_text("ok\n", encoding="utf-8")


def main() -> int:
    event = read_input()
    event_name = str(event.get("hook_event_name") or "")
    if not event_name:
        event_name = "workspaceOpen" if "workspace_roots" in event else "sessionStart"

    notes: list[str] = []
    payload: dict = {}

    def finish(ok: str = "ok") -> int:
        summary = "personal-agent git sync: " + ("; ".join(notes) if notes else "nothing to do")
        if event_name == "sessionStart":
            payload["additional_context"] = summary
            payload["env"] = {"PERSONAL_AGENT_GIT_SYNC": ok}
        emit(payload)
        print(summary, file=sys.stderr)
        return 0

    root = workspace_root(event)
    if root is None or not root.exists():
        notes.append("skipped (no workspace)")
        return finish("skip")

    inside = git_ok(["rev-parse", "--is-inside-work-tree"], cwd=root)
    if inside != "true":
        notes.append("skipped (not a git checkout)")
        return finish("skip")

    toplevel = git_ok(["rev-parse", "--show-toplevel"], cwd=root)
    cwd = Path(toplevel) if toplevel else root
    origin = git_ok(["remote", "get-url", "origin"], cwd=cwd)
    if not origin:
        notes.append("skipped (no origin remote)")
        return finish("skip")

    branch = default_branch(cwd)
    common = git_ok(["rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=cwd) or str(cwd)

    try:
        if not should_skip_fetch(common):
            fetch = git(
                [
                    "fetch",
                    "--no-recurse-submodules",
                    "--no-tags",
                    "origin",
                    f"+refs/heads/{branch}:refs/remotes/origin/{branch}",
                ],
                cwd=cwd,
                timeout=80,
            )
            if fetch.returncode != 0:
                notes.append(f"fetch origin/{branch} failed (exit {fetch.returncode})")
                return finish("error")
            mark_fetched(common)
            notes.append(f"fetched origin/{branch}")
        else:
            notes.append(f"fetch skipped (origin/{branch} fetched recently)")
    except subprocess.TimeoutExpired:
        notes.append(f"fetch origin/{branch} timed out")
        return finish("error")

    remote_ref = f"origin/{branch}"
    if git(["show-ref", "--verify", "--quiet", f"refs/remotes/origin/{branch}"], cwd=cwd).returncode != 0:
        notes.append(f"skipped (no {remote_ref})")
        return finish("skip")

    canon = canon_path(cwd)
    if canon and canon.exists():
        canon_branch = git_ok(["branch", "--show-current"], cwd=canon) or ""
        if canon_branch == branch:
            behind = count_commits("HEAD", remote_ref, canon)
            if behind == 0:
                notes.append(f"canon {branch} already at {remote_ref}")
            elif has_tracked_dirty(canon):
                notes.append(f"skipped canon {branch} (tracked local changes)")
            else:
                merge = git(["merge", "--ff-only", remote_ref], cwd=canon)
                if merge.returncode == 0:
                    notes.append(f"fast-forwarded canon {branch} to {remote_ref}")
                else:
                    notes.append(f"canon {branch} fast-forward failed (exit {merge.returncode})")
        else:
            update = git(
                ["fetch", ".", f"{remote_ref}:refs/heads/{branch}"],
                cwd=cwd,
            )
            # Updating a checked-out branch from another worktree fails; try refspec fetch instead.
            if update.returncode != 0:
                update = git(
                    ["fetch", "--no-recurse-submodules", "--no-tags", "origin", f"refs/heads/{branch}:refs/heads/{branch}"],
                    cwd=cwd,
                )
            if update.returncode == 0:
                notes.append(f"updated local {branch} ref to {remote_ref}")
            else:
                notes.append(f"skipped local {branch} ref (checked out or not ff)")
    else:
        notes.append("skipped canon (could not resolve main worktree)")

    current = git_ok(["branch", "--show-current"], cwd=cwd) or ""
    if is_linked_worktree(cwd) and is_cursor_worktree(cwd, current) and current:
        unique = count_commits(remote_ref, "HEAD", cwd)
        behind = count_commits("HEAD", remote_ref, cwd)
        if unique > 0:
            notes.append(f"skipped this worktree (has {unique} commit(s) not on {remote_ref})")
        elif has_tracked_dirty(cwd):
            notes.append("skipped this worktree (tracked local changes)")
        elif behind == 0:
            notes.append(f"this worktree already at {remote_ref}")
        else:
            merge = git(["merge", "--ff-only", remote_ref], cwd=cwd)
            if merge.returncode == 0:
                notes.append(f"fast-forwarded this worktree to {remote_ref} ({behind} commit(s))")
            else:
                notes.append(f"this worktree fast-forward failed (exit {merge.returncode})")

    return finish("ok")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 — fail open
        emit({"additional_context": f"personal-agent git sync: aborted ({type(exc).__name__})"})
        raise SystemExit(0)
