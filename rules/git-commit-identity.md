---
description: Use an explicitly chosen Git identity without publishing machine-specific details.
trigger: always_on
---

# Git commit identity

Use the Git identity explicitly chosen by the user for the current repository. Honor machine-local and repository-specific preferences. Never substitute a GitHub login for a person's name or infer their email from a public profile.

If no identity is configured or the repository needs a different account, ask which name and email to use. Prefer per-command author and committer overrides; do not change global Git configuration.

Keep actual names, email addresses, credentials, and account-specific preferences in untracked machine-local configuration, not this public plugin. Never copy a work identity into a personal repository without approval.
