#!/usr/bin/env python3
import sys
try:
    import py_compile
    py_compile.compile('ui/dashboard_panel.py', doraise=True)
    print("✓ Syntax OK")
except SyntaxError as e:
    print(f"Syntax Error: {e}")
    print(f"Line: {e.lineno}")
    print(f"Text: {e.text}")
    sys.exit(1)
