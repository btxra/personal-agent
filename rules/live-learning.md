---
description: Persist durable discoveries only with user approval.
trigger: always_on
---

# Live learning

When a session produces reusable knowledge that future agents would otherwise rediscover, propose persisting it, but never write learning notes until the user approves.

Trigger only when all are true:
1. The knowledge is durable: a repository or tool convention, a lasting user correction, or a costly discovery about a path, flag, fixture, environment, or workflow.
2. It is not already documented in the relevant AGENTS.md, SKILL.md, or personal rules.
3. A future session would benefit.

Do not trigger for typos, one-off mistakes, transient errors, session-only debugging, secrets, credentials, personal information, production data, or facts already documented.

Before ending a completed workflow, non-trivial investigation, or user correction, evaluate the trigger. If it does not fire, write one short line: `No durable learning this session.`

## How to persist

1. Choose one canonical home: repository-wide facts in that repository's AGENTS.md; component facts in its scoped AGENTS.md; workflow facts in the existing SKILL.md; private preferences in untracked machine-local rules. Propose a new skill only when no suitable home exists.
2. State the discovery in one or two sentences, identify the single target file, and show a compact before/after snippet.
3. Ask the user to choose: "Approve and update now", "Edit the note first", or "Skip (session-only)". Use the available question tool, or ask in chat and wait. Revise and ask again after "Edit". Write nothing after "Skip".
4. After approval, edit only that file unless the user expanded scope. Match its style and prefer a small delta. Resume the original task afterward.

Never duplicate the same fact, mine archived threads, silently edit documentation, or publish learning to a shared or public repository without explicit approval. Do not edit installed plugin caches to save learning; use the appropriate source repository or private local rule instead.
