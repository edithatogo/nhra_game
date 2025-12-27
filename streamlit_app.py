"""
Streamlit Cloud Entrypoint

This file serves as the entry point for Streamlit Cloud deployment.
It imports and runs the main dashboard from scripts/dashboard.py.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and run the dashboard
from scripts.dashboard import main

if __name__ == "__main__":
    main()
