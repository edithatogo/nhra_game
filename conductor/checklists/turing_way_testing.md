# The Turing Way: Testing Checklist

Ref: <https://book.the-turing-way.org/reproducible-research/testing/testing-checklist>

## General Testing Practices

- [ ] **Unit Tests:** Are individual functions and classes tested in isolation?
- [ ] **Integration Tests:** Are interactions between modules/components tested?
- [ ] **Regression Tests:** Are there tests to ensure new changes don't break existing functionality?
- [ ] **Continuous Integration (CI):** Are tests run automatically on every commit/push?
- [ ] **Test Coverage:** Is code coverage measured and monitored?
- [ ] **Test Data:** Is synthetic or anonymized data used for testing to avoid privacy issues?
- [ ] **Documentation:** Are tests documented so others understand what they verify?

## Specific to Simulation/Scientific Code

- [ ] **Smoke Tests:** Do the scripts run from start to finish without crashing on a minimal dataset?
- [ ] **Sanity Checks:** Do the results make physical/logical sense (e.g., probabilities between 0 and 1)?
- [ ] **Deterministic Execution:** Can the results be exactly reproduced with a fixed random seed?
- [ ] **Edge Cases:** Are boundary conditions (e.g., zero inputs, max values) tested?
