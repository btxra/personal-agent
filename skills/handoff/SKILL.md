---
name: handoff
description: Write an explicitly requested, compact, redacted continuation note outside the repository.
argument-hint: "[what the next session should focus on]"
disable-model-invocation: true
triggers: [user]
license: MIT
---

# Handoff

Adapted from [Matt Pocock's handoff](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/handoff/SKILL.md). Copyright (c) 2026 Matt Pocock. [MIT license](../../licenses/matt-pocock-MIT.txt); [attribution and changes](../../THIRD_PARTY_NOTICES.md#matt-pocock-skills).

Use only when the user requests a handoff. Summarize the current authorized session; do not mine archived conversations, credential stores, unrelated repositories, or personal data to enrich it. This task does not authorize changes to repository guidance or sending the note to another service.

## Prepare

Read the current task state and identify the next session's focus. Reference existing specs, plans, diffs, issues, and commits instead of copying their contents. Keep facts, hypotheses, and blocked work distinct.

Include only what another session needs:

- Goal, scope, user decisions, and applicable constraints.
- Current repository/branch and relevant file paths or public links.
- Completed work and verification actually performed, including failures.
- Pending work, blockers, and the next concrete action.
- Existing server/process state only when necessary to continue safely.
- Suggested installed skills, if relevant; do not suggest unavailable tools as if they exist.

## Save privately

Use a unique new file in the operating system's temporary directory, not the repository or an installed plugin cache. On POSIX, create it with owner-only permissions (0600), for example through the language's secure temporary-file API. Never overwrite an existing handoff or user file. If a suitably private location is unavailable, report the limitation before saving sensitive context.

Redact credentials, tokens, authentication URLs, personal data, and unnecessary internal identifiers before writing. Preserve useful repository-relative references where possible. A local note still needs review before being shared. Do not paste raw logs, environment dumps, or network captures into it.

Check the saved note for sensitive content and accuracy. Return its path and a brief description of its focus. If the user asked only for a note in chat, return the redacted note without creating a file.
