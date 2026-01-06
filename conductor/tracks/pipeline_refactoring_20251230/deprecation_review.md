# Deprecation & Error Reconciliation Review

**Objective:** Review commented-out code to determine if it should be restored, refactored, or permanently deleted.

## Findings

### 1. `src/nhra_gt/domain/state.py`

**Code:**
```python
# JurisdictionState = JurisdictionStateJax  # FIXME: Ruff F811 Redefinition
```

**Context:**
`JurisdictionState` is defined as a class earlier in the file (lines 485+). The alias at the end of the file attempts to redefine it as `JurisdictionStateJax` (which is defined at line 500+).

**Analysis:**
This redefinition seems to be an attempt to use the JAX version as the default `JurisdictionState` alias at the module level, but it conflicts with the explicit class definition. If the intent is for `JurisdictionState` to *always* be the JAX version, the Pydantic/struct class definition should be renamed or removed. However, likely `JurisdictionState` (Pydantic/struct) serves a different purpose (e.g. legacy or non-JAX usage) than `JurisdictionStateJax`.

**Proposal:**
Keep commented out. If standard usage requires the JAX version, callers should import `JurisdictionStateJax` directly or we should rename the base class.

### 2. `src/nhra_gt/domain/params.py`

**Code:**
```python
# Queuing Utility (Preserving potentially duplicated/deprecated fields)
# queuing_outside_utility: float = -100.0  # Already defined above
# queuing_init_prob: float = 0.5           # Already defined above
```

**Context:**
These fields are defined in `OperationalParams` (lines 110-111) and then redefined in the same class (lines 120-121).

**Analysis:**
This is a strict duplication within the same class definition. The values are identical.

**Proposal:**
Safe to delete permanently. The fields exist and are initialized correctly in the first definition.

### 3. `src/nhra_gt/domain/params.py`

**Code:**
```python
# _data = self.model_dump()  # Preserved unused assignment
```

**Context:**
In `Params.replace`, `self.model_dump()` was called but the result `_data` was never used because the method proceeds to call `self.flatten()` which calls `model_dump()` internally.

**Analysis:**
Redundant computation. `flatten()` is the correct starting point for `from_flat_dict`.

**Proposal:**
Safe to delete permanently.

## Action Plan

1.  **Delete** the duplicated fields in `params.py`.
2.  **Delete** the unused assignment in `params.py`.
3.  **Investigate** `JurisdictionState` usage in the codebase. If `JurisdictionState` (the class) is used, keep the comment or remove the alias. If `JurisdictionStateJax` is the *only* intended state, refactor the class.
