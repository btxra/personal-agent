---
description: Keep updates to the user's own PRs in the description, not comments.
trigger: always_on
---

# Updates to our own PRs

Do not post comments or review-thread replies on a PR authored by the user or created on their behalf unless the user explicitly asks for that comment or reply. A request to fix, validate, push, or update a PR is not permission to comment.

Check the PR author against the user's relevant GitHub identity before posting. Do not assume the currently authenticated account is their only identity. If ownership is unclear, ask before commenting.

Put important changes to scope, validation results, or known limitations in the PR description. Skip routine progress updates, repeated test summaries, and commit-by-commit narration. Link to detailed evidence rather than copying logs into the description.

Read the current description before editing. Update the relevant section, preserve the template, required attribution, reviewer checklists, and unrelated content, and remove only superseded information. Do not append a running activity log or expose private data.

Follow the host's permission requirements for description edits. Do not delete existing comments unless the user explicitly requests it. This rule does not restrict authorized reviews of other people's PRs.
