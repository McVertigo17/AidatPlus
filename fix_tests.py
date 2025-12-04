#!/usr/bin/env python3

# Script to fix the failing tests in test_aidat_panel_run.py

def fix_test_file():
    # Read the file
    with open('tests/ui/test_aidat_panel_run.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Correct the syntax error in MockTab classes
    content = content.replace(
        'self.tk = SimpleNamespace(call=lambda *args: None), createcommand=lambda name, func: None',
        'self.tk = SimpleNamespace(call=lambda *args: None, createcommand=lambda name, func: None)'
    )
    
    # Fix 2: Remove the escaped characters from tag_configure method
    content = content.replace(
        'def tag_configure\\(self, tagname, \\*\\*kwargs\\):',
        'def tag_configure(self, tagname, **kwargs):'
    )
    
    # Write the file back
    with open('tests/ui/test_aidat_panel_run.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed the test file!")

if __name__ == "__main__":
    fix_test_file()