#!/usr/bin/env python3
"""Fix indentation issues in raporlar_panel.py"""

import re

# Read the file
with open('ui/raporlar_panel.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the problem area: line 2145 onwards should be dedented
# The issue is that everything after line 2142 (end of load_bos_konut_listesi) 
# is indented as if it's inside that method

lines = content.split('\n')

# Find the line number where the indentation problem starts
# Looking for the except block that ends load_bos_konut_listesi
for i, line in enumerate(lines):
    if i > 2140 and 'Removed setup_kategori_dagilimi_tab method' in line:
        print(f"Found problem at line {i+1}: {line[:60]}")
        print(f"Current indentation: {len(line) - len(line.lstrip())} spaces")
        
        # From this line onwards until EOF, dedent by 4 spaces if it's more than 4 spaces
        fixed_lines = []
        for j in range(len(lines)):
            if j < i:
                fixed_lines.append(lines[j])
            else:
                line_to_fix = lines[j]
                # Check if line starts with 8 or more spaces
                if line_to_fix.startswith('        ') and not line_to_fix.startswith('         '):
                    # Remove 4 spaces (one indent level)
                    fixed_lines.append(line_to_fix[4:])
                else:
                    fixed_lines.append(line_to_fix)
        
        # Write back
        with open('ui/raporlar_panel.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        
        print("Fixed indentation!")
        break
