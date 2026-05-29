# !/usr/bin/env python3
"""
Script to beautify Python code - improve formatting, docstrings, and structure
"""

import os
import re
from pathlib import Path

def improve_docstrings(content: str) -> str:
    """Improve docstring formatting and add missing docstrings"""
    lines = content.split('\n')
    improved_lines = []

    for i, line in enumerate(lines):
        # Improve Thai docstrings
        if '"""' in line and any(thai_char in line for thai_char in 'กขคงจฉชซฌญดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ'):
            # Keep Thai docstrings but improve formatting
            improved_lines.append(line)
        # Add English docstrings for functions without them
        elif line.strip().startswith('def ') and '(' in line and ':' in line:
            improved_lines.append(line)
            # Check if next line has docstring
            if i + 1 < len(lines) and '"""' not in lines[i + 1]:
                # Extract function name
                func_match = re.search(r'def\s+(\w+)', line)
                if func_match:
                    func_name = func_match.group(1)
                    indent = len(line) - len(line.lstrip())
                    docstring = f'{" " * (indent + 4)}"""{func_name.replace("_", " ").title()} function"""\n'
                    improved_lines.append(docstring)
        else:
            improved_lines.append(line)

    return '\n'.join(improved_lines)

def improve_variable_names(content: str) -> str:
    """Improve variable naming conventions"""
    # Replace common Thai variable names with English equivalents
    replacements = {
        # Keep existing replacements but add more professional ones
        'ผลลัพธ์': 'result',
        'ข้อมูล': 'data',
        'ไฟล์': 'file',
        'โมเดล': 'model',
        'ระบบ': 'system',
        'การตั้งค่า': 'config',
        'คำตอบ': 'response',
        'คำถาม': 'question',
        'ประเภท': 'type',
        'รายการ': 'list',
        'ตาราง': 'table',
        'คอลัมน์': 'column',
        'แถว': 'row',
        'ค่า': 'value',
        'ชื่อ': 'name',
        'เวลา': 'time',
        'วันที่': 'date',
        'ข้อผิดพลาด': 'error',
        'สถานะ': 'status',
        'จำนวน': 'count',
        'ขนาด': 'size',
        'ความยาว': 'length',
        'ตำแหน่ง': 'position',
        'ดัชนี': 'index',
    }

    for thai, english in replacements.items():
        # Replace in variable assignments but be careful with strings
        content = re.sub(rf'\b{thai}\b(?=\s*=)', english, content)

    return content

def improve_comments(content: str) -> str:
    """Improve comment formatting"""
    lines = content.split('\n')
    improved_lines = []

    for line in lines:
        if line.strip().startswith('#'):
            # Ensure space after #
            comment_match = re.match(r'^(\s*)#\s*(.+)', line)
            if comment_match:
                indent, comment_text = comment_match.groups()
                # Keep Thai comments but ensure proper formatting
                improved_line = f"{indent}# {comment_text}"
                improved_lines.append(improved_line)
            else:
                improved_lines.append(line)
        else:
            improved_lines.append(line)

    return '\n'.join(improved_lines)

def add_type_hints(content: str) -> str:
    """Add basic type hints where missing"""
    # Add typing imports if not present
    if 'from typing import' not in content and 'import typing' not in content:
        if 'import' in content:
            lines = content.split('\n')
            import_idx = -1
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_idx = i

            if import_idx >= 0:
                lines.insert(import_idx + 1, 'from typing import Dict, List, Optional, Any, Tuple')
                content = '\n'.join(lines)

    # Basic type hint improvements
    replacements = [
        (r'def (\w+)\(self, (\w+)\):', r'def \1(self, \2: str):'),
        (r'def (\w+)\((\w+)\):', r'def \1(\2: str):'),
        (r'def (\w+)\(self, (\w+), (\w+)\):', r'def \1(self, \2: str, \3: str):'),
        (r'-> dict:', r'-> Dict[str, Any]:'),
        (r'-> list:', r'-> List[Any]:'),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    return content

def improve_formatting(content: str) -> str:
    """Improve general code formatting"""
    # Remove trailing whitespace
    lines = content.split('\n')
    improved_lines = [line.rstrip() for line in lines]

    # Remove multiple empty lines
    final_lines = []
    empty_count = 0

    for line in improved_lines:
        if line.strip() == '':
            empty_count += 1
            if empty_count <= 2:  # Allow max 2 empty lines
                final_lines.append(line)
        else:
            empty_count = 0
            final_lines.append(line)

    # Ensure file ends with single newline
    while final_lines and final_lines[-1] == '':
        final_lines.pop()
    final_lines.append('')

    return '\n'.join(final_lines)

def beautify_file(file_path: Path) -> bool:
    """Beautify a single Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Apply improvements
        content = improve_docstrings(content)
        content = improve_comments(content)
        content = improve_formatting(content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Beautified: {file_path}")
            return True
        else:
            print(f"No changes: {file_path}")
            return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to beautify all Python files"""
    project_root = Path(__file__).parent.parent

    # Find all Python files (excluding .venv)
    python_files = []
    for pattern in ['**/*.py']:
        for file_path in project_root.glob(pattern):
            if '.venv' not in str(file_path) and '__pycache__' not in str(file_path):
                python_files.append(file_path)

    print(f"Found {len(python_files)} Python files to beautify")

    beautified_count = 0
    for file_path in python_files:
        if beautify_file(file_path):
            beautified_count += 1

    print(f"\nBeautification complete!")
    print(f"Files processed: {len(python_files)}")
    print(f"Files modified: {beautified_count}")
    print(f"Files unchanged: {len(python_files) - beautified_count}")

if __name__ == "__main__":
    main()


