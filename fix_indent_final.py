#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix all indentation in dashboard_panel.py"""

with open('ui/dashboard_panel.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for line in lines:
    # If line starts with 5 spaces + "def ", change to 4 spaces
    if line.startswith('     def '):
        line = '    ' + line[5:]
    # If line starts with 10+ spaces, convert to proper indentation
    elif line.startswith('          ') and not line.startswith('           '):
        line = '        ' + line[10:]
    
    fixed_lines.append(line)

with open('ui/dashboard_panel.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Fixed indentation!")
