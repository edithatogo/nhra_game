# Track Specification: WPI Health Data Automation (P2)

## 1. Overview

**Goal**: Automate the ingestion of ABS Wage Price Index (WPI) data for the Health care and social assistance sector, replacing hardcoded synthetic values.
**Context**: Derived from plan phases for wpi_health_data_automation_20251228.
**Constraints**: None explicitly stated in plan.

## 2. Functional Requirements

- Identify the exact SDMX Dataflow ID and Query Parameters for "WPI - Health care and social assistance". (ID: `ABS,WPI`, Key: `1.THRPEB.7.Q.10.AUS.Q`)
- Test API connectivity and response format (JSON/CSV) using `curl` or a test script. (CSV preferred)
- Create `src/nhra_gt/domain/abs_api.py` to handle ABS Data API requests.
- Implement parsing logic to extract the time series (Year, Value).
- Implement caching or local storage for the raw API response to avoid redundant calls.
- Update `scripts/data/ingest_economic_spine.py` to call the ABS API client.

## 3. Non-Functional Requirements

- Automated tests cover track changes.
- Validation checks pass for track changes.
- Verification steps are automated where possible.
- Automation scripts cover required workflows.
- CI checks are run and must pass.

## 4. Acceptance Criteria

- [ ] Identify the exact SDMX Dataflow ID and Query Parameters for "WPI - Health care and social assistance". (ID: `ABS,WPI`, Key: `1.THRPEB.7.Q.10.AUS.Q`)
- [ ] Test API connectivity and response format (JSON/CSV) using `curl` or a test script. (CSV preferred)
- [ ] Create `src/nhra_gt/domain/abs_api.py` to handle ABS Data API requests.
- [ ] Implement parsing logic to extract the time series (Year, Value).
- [ ] Relevant tests pass for track changes.

## Acceptance Checklist (Evaluation)

- [ ] Requirements and scope validated against this spec
- [ ] Acceptance criteria evaluated and recorded (pass/fail)
- [ ] CI green and key workflows verified
- [ ] Deployment/runtime checks complete (if applicable)
- [ ] Deviations or follow-ups documented
