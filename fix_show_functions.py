#!/usr/bin/env python3
import re
import sys

def fix_ui_files():
    """Fix show_error, show_warning, show_success fonksiyon çağrılarını düzelt"""
    
    files = [
        'ui/sakin_panel.py',
        'ui/lojman_panel.py',
        'ui/aidat_panel.py',
        'ui/finans_panel.py',
        'ui/ayarlar_panel.py'
    ]
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Pattern 1: show_error("title", "message", parent=modal)
            content = re.sub(
                r'show_error\("([^"]+)",\s*"([^"]+)",\s*parent=modal\)',
                r'show_error(parent=modal, title="\1", message="\2")',
                content
            )
            
            # Pattern 2: show_error("title", f"message...", parent=modal)
            content = re.sub(
                r'show_error\("([^"]+)",\s*(f"[^"]*(?:\{[^}]*\}[^"]*)*"),\s*parent=modal\)',
                r'show_error(parent=modal, title="\1", message=\2)',
                content
            )
            
            # Pattern 3: show_error("title", str(e.message), parent=modal)
            content = re.sub(
                r'show_error\("([^"]+)",\s*(str\([^)]+\)),\s*parent=modal\)',
                r'show_error(parent=modal, title="\1", message=\2)',
                content
            )
            
            # Pattern 4: show_error("title", f"message", parent=modal) with multiple lines
            content = re.sub(
                r'show_error\("([^"]+)",\s*(f"[^"]*\{[^}]*\}[^"]*"),\s*parent=modal\)',
                r'show_error(parent=modal, title="\1", message=\2)',
                content
            )
            
            # Pattern 5: show_success("title", message, parent=modal) - basit
            content = re.sub(
                r'show_success\("([^"]+)",\s*"([^"]+)",\s*parent=modal\)',
                r'show_success(parent=modal, title="\1", message="\2")',
                content
            )
            
            # Pattern 6: show_success("title", f"message", parent=modal)
            content = re.sub(
                r'show_success\("([^"]+)",\s*(f"[^"]*(?:\{[^}]*\}[^"]*)*"),\s*parent=modal\)',
                r'show_success(parent=modal, title="\1", message=\2)',
                content
            )
            
            # Pattern 7: show_warning(..., parent=modal) 
            content = re.sub(
                r'show_warning\("([^"]+)",\s*"([^"]+)",\s*parent=modal\)',
                r'show_warning(parent=modal, title="\1", message="\2")',
                content
            )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'[OK] {file_path} duzeltildi')
            else:
                print(f'[SKIP] {file_path} zaten duzeltilmis')
        
        except Exception as e:
            print(f'[ERROR] {file_path} duzeltilirken hata: {e}')

if __name__ == '__main__':
    fix_ui_files()
    print("\nDüzeltme işleri tamamlandı!")
