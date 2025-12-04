#!/usr/bin/env python3
"""Quick syntax check"""
import sys
import py_compile

try:
    py_compile.compile('ui/raporlar_panel.py', doraise=True)
    print("✓ File compiles successfully")
    sys.exit(0)
except py_compile.PyCompileError as e:
    print(f"✗ Syntax error found:\n{e}")
    sys.exit(1)
