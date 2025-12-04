#!/usr/bin/env python3
"""
Simple heuristic scanner to find occurrences of `db = get_db()` and report if there is no `db.close()` or `session.close()` within the same function scope.
This helps identify functions likely to leak DB sessions.

Usage:
    python scripts/check_db_close.py

"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CALL_RE = re.compile(r"\b(db|session)\s*=\s*get_db\(\)")
DB_CLOSE_RE = re.compile(r"\b(db|session)\.close\s*\(")
CLASS_CLOSE_RE = re.compile(r"self\._close_db\s*\(")
CTX_RE = re.compile(r"with\s+(get_db\(\)|SessionLocal\(\))")

def remove_triple_quoted_blocks(text: str) -> str:
    # Remove triple-quoted strings (both single and double quotes) to avoid docstring false positives
    import re
    pattern = re.compile(r"('''.*?'''|\"\"\".*?\"\"\")", re.DOTALL)
    return pattern.sub('', text)


def find_functions_with_get_db(file_path: Path):
    results = []
    text = file_path.read_text(encoding='utf-8')
    # Remove triple-quoted docstrings to avoid get_db matches in comments/docs
    text = remove_triple_quoted_blocks(text)
    # Split into lines and function blocks
    lines = text.splitlines()
    # Find lines with 'def ' to identify functions
    func_start_indices = [i for i,l in enumerate(lines) if l.strip().startswith('def ')]
    func_boundaries = func_start_indices + [len(lines)]

    for idx in func_start_indices:
        start = idx
        end = next((b for b in func_boundaries if b > start+0), len(lines))
        block = '\n'.join(lines[start:end])
        # extract function name
        first_line = lines[start].strip()
        m = re.match(r'def\s+(\w+)\s*\(', first_line)
        func_name = m.group(1) if m else ''
        # Ignore helper _get_db functions or trivial getters
        if func_name in ('_get_db', 'get_db', 'get_db_session'):
            continue
        if CALL_RE.search(block):
            if DB_CLOSE_RE.search(block) or CTX_RE.search(block) or CLASS_CLOSE_RE.search(block):
                pass
            else:
                results.append((start+1, block))
    return results

def main():
    py_files = list(ROOT.rglob('**/*.py'))
    suspect = []
    for p in py_files:
        # skip tests and envs and the script itself
        if 'site-packages' in str(p) or 'scripts' in str(p) and p.name == 'check_db_close.py':
            continue
        results = find_functions_with_get_db(p)
        if results:
            suspect.append((p, [pos for pos,_ in results]))

    if not suspect:
        print('No suspicious get_db() usage detected without db.close() or with-context in functions')
    else:
        print('Found suspicious get_db() uses (no close/context detected) at:')
        for p, positions in suspect:
            print(f'  {p} -> function starts at lines: {positions}')

if __name__ == '__main__':
    main()
