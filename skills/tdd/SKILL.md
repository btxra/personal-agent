---
name: tdd
description: Implement explicitly requested behavior test-first through a public interface, one small slice at a time.
argument-hint: "<behavior to implement or bug to fix test-first>"
disable-model-invocation: true
triggers: [user]
license: MIT
---

# Test-driven development

Adapted from [Matt Pocock's TDD skill](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/tdd). Copyright (c) 2026 Matt Pocock. [MIT license](../../licenses/matt-pocock-MIT.txt); [attribution and changes](../../THIRD_PARTY_NOTICES.md#matt-pocock-skills).

Use this workflow only when explicitly requested. Work within the user's change scope and repository conventions. It does not authorize dependency installation, production operations, commits, pushes, or unrelated refactors.

## Choose the behavior and boundary

Identify the observable behavior, its expected outcome, and the public interface that exposes it. Reuse existing tests and helpers where suitable. Read [test boundaries and doubles](references/testing.md) before choosing a seam.

Use acceptance criteria and decisions already supplied by the user. Ask only when a material behavior or interface choice remains unresolved; do not require repeated approval for settled choices. State what the chosen boundary covers and what it cannot establish.

## One slice per cycle

1. Write one focused test for the next behavior. Derive expected values from the requirement or an independently worked example, never by repeating the implementation's calculation.
2. Run that test before implementing. Confirm it fails because the requested behavior is missing or broken, not because imports, credentials, infrastructure, or fixtures are invalid. If it already passes, reassess the gap rather than manufacturing a failure in production code.
3. Add the smallest implementation that satisfies that behavior. Keep unrelated changes out.
4. Run the same test and observe it pass. Then run the directly affected tests that cover meaningful integration risks.
5. Repeat for the next behavior. Do not write a speculative batch of tests against an interface that has not been exercised.

Refactor only when needed for this change, after the relevant tests are green. Re-run those checks after the refactor. Avoid creating tests for trivial or reversible edits where they provide no useful behavioral protection.

Use synthetic data and authorized local/test resources. Keep secrets out of fixtures, snapshots, output, and commits. If execution is blocked, say that the tests were not run; writing a test is not evidence that it fails or passes.

## Report

Summarize the behavior, public boundaries covered, red-to-green evidence actually observed, relevant commands/results, and remaining gaps. Do not claim performance, coverage, or behavioral guarantees that were not measured.
