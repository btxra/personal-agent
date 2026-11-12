# Personal Agent

<img src="assets/personal-agent.svg" alt="Personal Agent icon" width="96" height="96">

Personal rules, focused engineering skills, and safe Git worktree synchronization for Cursor and Devin.

## Install

In Cursor, open **Customize → Plugins → From GitHub Repository**, add `btxra/personal-agent`, and enable `personal-agent` from the marketplace.

In Devin, add `btxra/personal-agent` from **Customize → Plugins**, or run:

```sh
devin plugins install btxra/personal-agent
```

Do not add `--local` if you want the installation recorded in your personal cloud plugin manifest. Hooks run in local Cursor and Devin IDE/CLI sessions, not cloud sessions. Remove or disable older machine-local installations only after confirming the repository-backed plugin is installed, to avoid duplicate hooks.

## Behavior

- Use the user's chosen Git identity without embedding names or email addresses in the plugin.
- Write short, plain, conversational text by default, without filler or canned agent phrasing.
- Keep important updates to the user's own PRs in the description, not comments, unless a comment is explicitly requested.
- Ask for approval before persisting durable learning.
- Fetch the default branch and fast-forward eligible clean checkouts and fresh agent worktrees. Never hard-reset or force-update local branches.

Git synchronization runs automatically at session start (and workspace open in Cursor). It can modify clean default-branch checkouts and fresh agent worktrees. See the worktree rule for eligibility and safeguards.

Requires Git and Python 3.10+. There are no third-party Python dependencies. State is stored outside the installed plugin at `$XDG_STATE_HOME/personal-agent`, defaulting to `~/.local/state/personal-agent`.

Keep private identities and account preferences in your IDE's machine-local rules. Do not commit local configuration, tokens, backups, or state to this repository.

## Optional skills

The skills run only when explicitly invoked; they do not add another always-on workflow. In Devin, use the namespaced commands below. In Cursor, select the matching skill from the installed plugin's command picker.

| Command | Purpose |
| --- | --- |
| `/personal-agent:diagnose` | Reproduce a bug, compare explanations, and report evidence. Fixes require an authorized fix request. |
| `/personal-agent:tdd` | Implement requested behavior through a public interface, one red-to-green slice at a time. |
| `/personal-agent:handoff` | Create a compact, redacted continuation note outside the repository, or in chat when requested. |
| `/personal-agent:ui-polish` | Audit a screen, agree a direction, refine it, and verify what renders. |

These skills respect repository instructions and host permissions. They do not grant permission to install tools, use production systems, publish artifacts, or change GitHub accounts. UI polish uses existing browser tooling and reports when runtime verification is unavailable. Desloppify is not included.

Captured pages, private screenshots, handoffs, and reports belong in a private temporary directory outside the repository. The plugin does not upload these artifacts or connect image-generation services.

## License and credits

Original material is [MIT-licensed](LICENSE). The engineering and handoff skills are adapted from Matt Pocock's MIT-licensed skills; UI polish is adapted from Damir Sokolovsky's Unslop under CC BY 4.0. See [third-party notices](THIRD_PARTY_NOTICES.md) for pinned revisions, retained licenses, file mappings, and modifications.

## Updates and tests

Use the IDE's plugin update controls. For Devin, run `devin plugins update personal-agent`; use Customize's reindex action if its cloud listing is stale. Update the repository's rule pairs together: `.md` is for Devin and `.mdc` for Cursor, with identical bodies.

```sh
python3 -m unittest discover -s tests -v
```

CI checks plugin packaging and unit tests, and scans Git history for secrets with a pinned Gitleaks release. These checks do not establish agent-behavior effectiveness; that requires isolated runs with and without the skill. GitHub secret scanning and push protection complement CI.
