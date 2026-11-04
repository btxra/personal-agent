# Personal Agent

Personal rules and safe Git worktree synchronization for Cursor and Devin.

## Install

In Cursor, open **Customize → Plugins → From GitHub Repository**, add `btxra/personal-agent`, and enable `personal-agent` from the marketplace.

In Devin, add `btxra/personal-agent` from **Customize → Plugins**, or run:

```sh
devin plugins install btxra/personal-agent
```

Do not add `--local` if you want the installation recorded in your personal cloud plugin manifest. Hooks run in local Cursor and Devin IDE/CLI sessions, not cloud sessions. Remove or disable older machine-local installations only after confirming the repository-backed plugin is installed, to avoid duplicate hooks.

## Behavior

- Use the user's chosen Git identity without embedding names or email addresses in the plugin.
- Ask for approval before persisting durable learning.
- Fetch the default branch and fast-forward eligible clean checkouts and fresh agent worktrees. Never hard-reset or force-update local branches.

Git synchronization runs automatically at session start (and workspace open in Cursor). It can modify clean default-branch checkouts and fresh agent worktrees. See the worktree rule for eligibility and safeguards.

Requires Git and Python 3.10+. There are no third-party Python dependencies. State is stored outside the installed plugin at `$XDG_STATE_HOME/personal-agent`, defaulting to `~/.local/state/personal-agent`.

Keep private identities and account preferences in your IDE's machine-local rules. Do not commit local configuration, tokens, backups, or state to this repository.

## Updates and tests

Use the IDE's plugin update controls. For Devin, run `devin plugins update personal-agent`; use Customize's reindex action if its cloud listing is stale. Update the repository's rule pairs together: `.md` is for Devin and `.mdc` for Cursor, with identical bodies.

```sh
python3 -m unittest discover -s tests -v
```
