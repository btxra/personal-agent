---
name: diagnose
description: Diagnose an explicitly requested bug with a reproducible failure, competing explanations, and evidence.
argument-hint: "<symptom and relevant code or reproduction>"
disable-model-invocation: true
triggers: [user]
license: MIT
---

# Diagnose

Adapted from [Matt Pocock's diagnosing-bugs](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/diagnosing-bugs/SKILL.md). Copyright (c) 2026 Matt Pocock. [MIT license](../../licenses/matt-pocock-MIT.txt); [attribution and changes](../../THIRD_PARTY_NOTICES.md#matt-pocock-skills).

Use this workflow only when the user invokes it or explicitly requests it. Invocation authorizes diagnosis; edit production source only when a fix is also requested. Follow the repository's instructions and the host's permissions. This skill does not authorize deployments, production probes, commits, pushes, or external messages.

## 1. Establish a useful reproduction

Read the reported symptom, nearby code, existing tests, and relevant architecture decisions. Separate observed facts from assumptions. Choose the narrowest available check that exercises the actual failing path: a test, local CLI command, request against a test service, or browser interaction.

Run it and record the expected result, observed result, command, and environment. A successful startup is not a reproduction of a functional failure. For intermittent failures, record the attempts and conditions instead of describing the check as deterministic.

Use authorized local/test environments and synthetic fixtures. Keep credentials in the environment and redact captured output before displaying or saving it. Do not capture real user data, authentication headers, or full network traces unnecessarily. Keep necessary private artifacts outside version control.

If access or a suitable reproduction is unavailable, report the blocker and the smallest next check. You may continue read-only investigation, but label explanations as hypotheses and do not claim a confirmed cause.

## 2. Narrow the cause

Reduce the reproduction one change at a time while preserving the user's symptom. State the plausible competing causes and a discriminating observation for each; do not invent alternatives just to fill a quota.

Test one explanation at a time using narrow assertions, debugger inspection, or temporary instrumentation. Read-only evidence collection is preferable to broad logging. For performance bugs, compare measurements under the same conditions and report the measurement method.

Confirm the cause only when evidence shows the relevant path executes in the failing scenario. Agreement on the symptom alone is not evidence for a mechanism.

## 3. Fix only within the authorized scope

If a fix was requested, turn the reproduction into a regression test at a real public boundary where practical. Observe it fail for the reported reason, make the smallest justified fix, then observe it pass. If no meaningful test seam exists, explain the coverage gap rather than writing an assertion that cannot catch the bug.

Run the original scenario again and the narrow related checks needed to resolve remaining risk. Remove only temporary instrumentation and artifacts created for this investigation; preserve the user's changes.

## Report

Give the observed symptom, confirmed cause or remaining hypotheses, supporting evidence, changed files if any, and verification results. Distinguish checks actually run from suggested checks. Include limitations and the next discriminating check if blocked. Redact sensitive values.
