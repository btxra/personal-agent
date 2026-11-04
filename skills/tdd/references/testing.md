# Test boundaries and doubles

Adapted from Matt Pocock's [test examples](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/tdd/tests.md) and [mocking guidance](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/tdd/mocking.md). Copyright (c) 2026 Matt Pocock. [MIT license](../../../licenses/matt-pocock-MIT.txt).

A useful test observes behavior through an interface a real caller uses. Internal classes, call order, and private methods can change while that behavior stays correct.

- For a creation API, create through the API and retrieve through its supported read interface. Inspect internal storage only when storage itself is the contract under test.
- For a calculation over inputs 10 and 5, an independently established expected result of 15 can catch mistakes. Recomputing the expectation with the same loop as the implementation cannot establish independent correctness.
- Name the capability or failure being tested, not the internal calls used to achieve it.
- Prefer the repository's existing integration fixtures and local test services when they make the check dependable and reasonably fast.

Use test doubles at boundaries such as remote services, time, randomness, and external side effects. A payment test must not charge a real account. Prefer a deterministic fake or test service to mocking a chain of internal collaborators.

Pass external dependencies through the project's existing injection boundary where available. Avoid redesigning unrelated code solely to make a test easier. State which real integration behavior a fake does not exercise.
