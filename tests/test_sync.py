import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "hooks" / "scripts"
SENTINEL = "token=SENTINEL_PRIVATE"


def load_engine():
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec = importlib.util.spec_from_file_location("sync_origin_main", SCRIPTS / "sync_origin_main.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path.remove(str(SCRIPTS))


def git_env(extra=None):
    env = dict(os.environ)
    env.update({
        "GIT_AUTHOR_NAME": "Test User",
        "GIT_AUTHOR_EMAIL": "test@example.invalid",
        "GIT_COMMITTER_NAME": "Test User",
        "GIT_COMMITTER_EMAIL": "test@example.invalid",
        "GIT_TERMINAL_PROMPT": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    if extra:
        env.update(extra)
    return env


def sh(*args, cwd=None, env=None):
    r = subprocess.run(args, cwd=cwd, env=env or git_env(), text=True, capture_output=True)
    assert r.returncode == 0, f"{args}: {r.stderr}"
    return r.stdout.strip()


def make_repo(base, default="main"):
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    remote = base / "remote.git"
    seed = base / "seed"
    canon = base / "canon"
    sh("git", "init", "--bare", "-b", default, str(remote))
    sh("git", "init", "-b", default, str(seed))
    (seed / "f.txt").write_text("A\n")
    sh("git", "-C", str(seed), "add", ".")
    sh("git", "-C", str(seed), "commit", "-m", "A")
    sh("git", "-C", str(seed), "remote", "add", "origin", str(remote))
    sh("git", "-C", str(seed), "push", "-u", "origin", default)
    sh("git", "clone", str(remote), str(canon))
    (seed / "f.txt").write_text("B\n")
    (seed / "newfile.txt").write_text("new\n")
    sh("git", "-C", str(seed), "add", ".")
    sh("git", "-C", str(seed), "commit", "-m", "B")
    sh("git", "-C", str(seed), "push")
    sha_a = sh("git", "-C", str(canon), "rev-parse", "HEAD")
    sha_b = sh("git", "-C", str(seed), "rev-parse", "HEAD")
    return remote, seed, canon, sha_a, sha_b


def head(p):
    return sh("git", "-C", str(p), "rev-parse", "HEAD")


class EngineCase(unittest.TestCase):
    def setUp(self):
        self.engine = load_engine()
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.engine.LOCK_DIR = Path(self.td.name) / "state"
        self._env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)

    def run_engine(self, root, stdin_text=None):
        os.environ["CURSOR_PROJECT_DIR"] = str(root)
        event = {"hook_event_name": "sessionStart"} if stdin_text is None else None
        oldin = sys.stdin
        sys.stdin = io.StringIO(stdin_text if stdin_text is not None else json.dumps(event))
        out, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = self.engine.main()
        finally:
            sys.stdin = oldin
        line = out.getvalue().strip()
        return rc, (json.loads(line) if line else None), err.getvalue()

    def ctx(self, payload):
        return payload["additional_context"]

    def test_non_git_skip(self):
        rc, p, e = self.run_engine(self.td.name)
        self.assertEqual(rc, 0)
        self.assertIn("not a git checkout", self.ctx(p))
        self.assertEqual(p["env"]["PERSONAL_AGENT_GIT_SYNC"], "skip")

    def test_clean_canon_and_agent_worktree_ff(self):
        remote, seed, canon, a, b = make_repo(Path(self.td.name) / "r")
        wt = canon / ".windsurf" / "worktrees" / "wt1"
        sh("git", "-C", str(canon), "worktree", "add", "-b", "windsurf/wt1", str(wt), a)
        rc, p, e = self.run_engine(wt)
        self.assertEqual(head(canon), b)
        self.assertEqual(head(wt), b)
        self.assertIn("fast-forwarded", self.ctx(p))

    def test_dirty_canon_and_worktree_unchanged(self):
        remote, seed, canon, a, b = make_repo(Path(self.td.name) / "r")
        wt = canon / ".cursor" / "worktrees" / "wt1"
        sh("git", "-C", str(canon), "worktree", "add", "-b", "cursor/wt1", str(wt), a)
        (canon / "f.txt").write_text("dirty\n")
        (wt / "f.txt").write_text("dirty\n")
        rc, p, e = self.run_engine(wt)
        self.assertEqual(head(canon), a)
        self.assertEqual(head(wt), a)

    def test_unique_commit_worktree_unchanged(self):
        remote, seed, canon, a, b = make_repo(Path(self.td.name) / "r")
        wt = canon / ".devin" / "worktrees" / "wt1"
        sh("git", "-C", str(canon), "worktree", "add", "-b", "devin/wt1", str(wt), a)
        (wt / "u.txt").write_text("u\n")
        sh("git", "-C", str(wt), "add", ".")
        sh("git", "-C", str(wt), "commit", "-m", "U")
        rc, p, e = self.run_engine(wt)
        self.assertEqual(head(canon), b)
        self.assertEqual(sh("git", "-C", str(wt), "rev-list", "--count", f"{b}..HEAD"), "1")

    def test_non_agent_worktree_unchanged(self):
        remote, seed, canon, a, b = make_repo(Path(self.td.name) / "r")
        wt = Path(self.td.name) / "otherwt"
        sh("git", "-C", str(canon), "worktree", "add", "-b", "feature/x", str(wt), a)
        rc, p, e = self.run_engine(wt)
        self.assertEqual(head(wt), a)
        self.assertEqual(head(canon), b)

    def test_untracked_collision_preserved(self):
        remote, seed, canon, a, b = make_repo(Path(self.td.name) / "r")
        wt = canon / ".cursor" / "worktrees" / "wt1"
        sh("git", "-C", str(canon), "worktree", "add", "-b", "cursor/wt1", str(wt), a)
        (wt / "newfile.txt").write_text("local-untracked\n")
        rc, p, e = self.run_engine(wt)
        self.assertEqual((wt / "newfile.txt").read_text(), "local-untracked\n")
        self.assertEqual(head(wt), a)

    def test_master_default(self):
        remote, seed, canon, a, b = make_repo(Path(self.td.name) / "r", default="master")
        rc, p, e = self.run_engine(canon)
        self.assertEqual(head(canon), b)
        self.assertIn("origin/master", self.ctx(p))

    def test_malformed_stdin_tolerated(self):
        remote, seed, canon, a, b = make_repo(Path(self.td.name) / "r")
        rc, p, e = self.run_engine(canon, stdin_text="not json{{")
        self.assertEqual(rc, 0)
        self.assertEqual(head(canon), b)

    def test_fetch_ttl_skip(self):
        remote, seed, canon, a, b = make_repo(Path(self.td.name) / "r")
        rc, p1, e = self.run_engine(canon)
        rc, p2, e = self.run_engine(canon)
        self.assertIn("fetched recently", self.ctx(p2))

    def test_failed_status_aborts(self):
        remote, seed, canon, a, b = make_repo(Path(self.td.name) / "r")
        orig = self.engine.git

        def fake(args, cwd=None, timeout=60):
            if args and args[0] == "status":
                return subprocess.CompletedProcess(args, 1, "", "boom")
            return orig(args, cwd=cwd, timeout=timeout)

        self.engine.git = fake
        try:
            with self.assertRaises(RuntimeError):
                self.run_engine(canon)
        finally:
            self.engine.git = orig
        self.assertEqual(head(canon), a)

    def test_failed_revlist_aborts(self):
        remote, seed, canon, a, b = make_repo(Path(self.td.name) / "r")
        orig = self.engine.git_ok

        def fake(args, cwd=None, timeout=60):
            if args and args[0] == "rev-list":
                return None
            return orig(args, cwd=cwd, timeout=timeout)

        self.engine.git_ok = fake
        try:
            with self.assertRaises(RuntimeError):
                self.run_engine(canon)
        finally:
            self.engine.git_ok = orig
        self.assertEqual(head(canon), a)

    def test_fetch_failure_no_stderr_leak(self):
        remote, seed, canon, a, b = make_repo(Path(self.td.name) / "r")
        orig = self.engine.git

        def fake(args, cwd=None, timeout=60):
            if args and args[0] == "fetch" and "origin" in args:
                return subprocess.CompletedProcess(args, 128, "", f"fatal: {SENTINEL}")
            return orig(args, cwd=cwd, timeout=timeout)

        self.engine.git = fake
        try:
            rc, p, e = self.run_engine(canon)
        finally:
            self.engine.git = orig
        self.assertIn("failed (exit 128)", self.ctx(p))
        self.assertNotIn(SENTINEL, self.ctx(p))
        self.assertNotIn(SENTINEL, e)

    def test_agent_worktree_detection(self):
        f = self.engine.is_cursor_worktree
        self.assertTrue(f(Path("/x/.cursor/worktrees/y"), "f"))
        self.assertTrue(f(Path("/x/.windsurf/worktrees/y"), "f"))
        self.assertTrue(f(Path("/x/.devin/worktrees/y"), "f"))
        self.assertTrue(f(Path("/x/y"), "cursor/a"))
        self.assertTrue(f(Path("/x/y"), "windsurf/a"))
        self.assertTrue(f(Path("/x/y"), "devin/a"))
        self.assertFalse(f(Path("/x/.cursor/other/worktrees"), "f"))
        self.assertFalse(f(Path("/x/wt"), "feature/x"))


class EntrypointCase(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)

    def run_script(self, name, stdin_text, env_extra):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / name)],
            input=stdin_text, text=True, capture_output=True,
            env=git_env(env_extra), cwd=self.td.name,
        )

    def test_cursor_session_start_non_git(self):
        d = Path(self.td.name) / "plain"
        d.mkdir()
        r = self.run_script("sync-cursor.py", '{"hook_event_name":"sessionStart"}',
                            {"CURSOR_PROJECT_DIR": str(d)})
        self.assertEqual(r.returncode, 0)
        p = json.loads(r.stdout.strip())
        self.assertIn("not a git checkout", p["additional_context"])
        self.assertEqual(p["env"]["PERSONAL_AGENT_GIT_SYNC"], "skip")

    def test_cursor_workspace_open_non_git(self):
        d = Path(self.td.name) / "plain"
        d.mkdir()
        r = self.run_script("sync-cursor.py", json.dumps({"workspace_roots": [str(d)]}), {})
        self.assertEqual(r.returncode, 0)
        p = json.loads(r.stdout.strip())
        self.assertNotIn("additional_context", p)
        self.assertIn("not a git checkout", r.stderr)

    def test_devin_session_start_non_git(self):
        d = Path(self.td.name) / "plain"
        d.mkdir()
        r = self.run_script("sync-devin.py", '{"hook_event_name":"SessionStart"}',
                            {"DEVIN_PROJECT_DIR": str(d)})
        self.assertEqual(r.returncode, 0)
        p = json.loads(r.stdout.strip())
        ctx = p["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(p["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertIn("not a git checkout", ctx)

    def test_xdg_state_path_outside_source(self):
        remote, seed, canon, a, b = make_repo(Path(self.td.name) / "r")
        xdg = Path(self.td.name) / "xdg"
        r = self.run_script("sync-cursor.py", '{"hook_event_name":"sessionStart"}',
                            {"CURSOR_PROJECT_DIR": str(canon), "XDG_STATE_HOME": str(xdg)})
        self.assertEqual(r.returncode, 0)
        self.assertEqual(head(canon), b)
        stamps = list((xdg / "personal-agent").glob("*.fetched"))
        self.assertEqual(len(stamps), 1)

    def test_subprocess_fetch_failure_no_leak(self):
        remote, seed, canon, a, b = make_repo(Path(self.td.name) / "r")
        fakebin = Path(self.td.name) / "bin"
        fakebin.mkdir()
        real_git = sh("which", "git")
        (fakebin / "git").write_text(
            "#!/bin/sh\n"
            'for a in "$@"; do\n'
            '  if [ "$a" = "fetch" ]; then\n'
            f'    echo "fatal: {SENTINEL}" >&2; exit 128\n'
            "  fi\n"
            "done\n"
            f'exec "{real_git}" "$@"\n'
        )
        (fakebin / "git").chmod(0o755)
        env = git_env({"CURSOR_PROJECT_DIR": str(canon),
                       "PATH": f"{fakebin}{os.pathsep}{os.environ['PATH']}",
                       "XDG_STATE_HOME": str(Path(self.td.name) / 'xdg')})
        r = subprocess.run([sys.executable, str(SCRIPTS / "sync-cursor.py")],
                           input='{"hook_event_name":"sessionStart"}', text=True,
                           capture_output=True, env=env, cwd=str(canon))
        self.assertEqual(r.returncode, 0)
        p = json.loads(r.stdout.strip())
        self.assertIn("failed (exit 128)", p["additional_context"])
        self.assertNotIn("SENTINEL", r.stdout + r.stderr)
        self.assertEqual(head(canon), a)


class StaticFileCase(unittest.TestCase):
    def test_rule_bodies_match(self):
        for stem in ("git-commit-identity", "live-learning", "worktree-from-origin"):
            md = (REPO_ROOT / "rules" / f"{stem}.md").read_text()
            mdc = (REPO_ROOT / "rules" / f"{stem}.mdc").read_text()
            self.assertTrue(md.startswith("---\n"), stem)
            self.assertIn("trigger: always_on", md.split("---", 2)[1])
            self.assertIn("alwaysApply: true", mdc.split("---", 2)[1])
            self.assertEqual(md.split("---", 2)[2], mdc.split("---", 2)[2], stem)

    def test_manifests_consistent(self):
        cur = json.loads((REPO_ROOT / ".cursor-plugin" / "plugin.json").read_text())
        dev = json.loads((REPO_ROOT / ".devin-plugin" / "plugin.json").read_text())
        mkt = json.loads((REPO_ROOT / ".cursor-plugin" / "marketplace.json").read_text())
        self.assertEqual(cur["name"], "personal-agent")
        self.assertEqual(dev["name"], "personal-agent")
        self.assertEqual(cur["version"], dev["version"])
        self.assertEqual(cur["version"], mkt["version"])
        self.assertEqual(mkt["plugins"][0]["name"], "personal-agent")
        self.assertEqual(mkt["plugins"][0]["source"], "./")

    def test_hook_targets_exist(self):
        dj = json.loads((REPO_ROOT / "hooks.json").read_text())
        cmd = dj["SessionStart"][0]["hooks"][0]["command"]
        self.assertIn("${DEVIN_PLUGIN_ROOT}/hooks/scripts/sync-devin.py", cmd)
        self.assertTrue((SCRIPTS / "sync-devin.py").exists())
        cj = json.loads((REPO_ROOT / "hooks" / "hooks.cursor.json").read_text())
        for event in ("workspaceOpen", "sessionStart"):
            cmd = cj["hooks"][event][0]["command"]
            self.assertIn("${CURSOR_PLUGIN_ROOT}/hooks/scripts/sync-cursor.py", cmd)
        self.assertTrue((SCRIPTS / "sync-cursor.py").exists())
        self.assertTrue((SCRIPTS / "sync_origin_main.py").exists())


if __name__ == "__main__":
    unittest.main()
