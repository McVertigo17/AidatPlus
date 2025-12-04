# Script to fix syntax error in test file
with open('tests/ui/test_dashboard_panel_run.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the syntax error by adding a newline
lines[1829] = '        assert isinstance(gider_list[0], (int, float))\n\n'

with open('tests/ui/test_dashboard_panel_run.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Fixed syntax error in test file")