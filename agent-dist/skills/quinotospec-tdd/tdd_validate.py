#!/usr/bin/env python3
"""Wrapper TDD gate — delega en rules-enforce/tdd_validate.py."""
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "quinotospec-rules-enforce" / "tdd_validate.py"
    raise SystemExit(subprocess.call([sys.executable, str(target)] + sys.argv[1:]))
