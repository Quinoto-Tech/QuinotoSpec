#!/usr/bin/env python3
import pathlib, re
proposals = list(pathlib.Path("agent-dist").glob("*"))
# demo rank
print("# | Propuesta | Score | Next")
print("1 | demo AUTH-a1b2 | 84 | ready")
