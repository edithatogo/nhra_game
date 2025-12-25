# Performance Profiling Guide

This project includes State-of-the-Art profiling tools to ensure computational efficiency as simulation rollouts scale.

## 1. Tools

### Pyinstrument (Recommended for Logic)
- **Use for:** High-level execution flow and finding bottlenecks in Python logic.
- **Output:** Clean, interactive HTML call trees.
- **Run:** `python scripts/profile_target.py <target> --profiler pyinstrument`

### Scalene (Recommended for Memory/GPU)
- **Use for:** Deep-dives into CPU, Memory, and GPU usage. It provides line-level precision.
- **Output:** Detailed HTML reports.
- **Run:** `python scripts/profile_target.py <target> --profiler scalene`

### Py-spy & Memray
- **Use for:** Low-level C-extension profiling and detailed memory leak analysis (advanced use cases).
- **Run:** Manual execution via `python -m py-spy` or `python -m memray`.

## 2. Profiling Targets

You can profile either a full module or a specific function:

- **Module:** `python scripts/profile_target.py scripts.run_baseline_v21`
- **Function:** `python scripts/profile_target.py scripts.run_baseline_v21:main`

## 3. Outputs
All profiling outputs are generated in the `./profiles/` directory, which is excluded from version control.
