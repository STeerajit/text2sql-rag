#!/usr/bin/env python3
"""
Safe script to remove emojis from Python files without breaking syntax
"""

import os
import re
import ast
from pathlib import Path

def is_valid_python(code: str) -> bool:
    """Check if Python code is syntactically valid"""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False

def safe_clean_emojis(content: str) -> str:
    """Safely remove emojis from Python code"""
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        original_line = line
        
        # Only process print statements and comments safely
        if 'print(' in line:
            # Handle print statements
            if 'print("' in line:
                # Extract the string content
                start = line.find('print("') + 7
                end = line.rfind('")')
                if end > start:
                    before = line[:start]
                    string_content = line[start:end]
                    after = line[end:]
                    
                    # Remove emojis from string content
                    clean_content = re.sub(r'[🚀📊🔍✅❌🧪📝🎯🔧📁💾🏠📦📈🔥⚡💡🎉🚨📋🤖⏱️📤🔄💾🗂️🛠️🗄️📚💻🎯🎭🏗️🔮📞📄🔍🎨📊🏆🤝📝📍📈🎯📱💼📚🔧⚙️🎛️📏🗃️📐📊⚡🎵🎨💫🌟⭐✨🎪🔤🤷‍♂️🔥💡✨] ', '', string_content)
                    
                    # Reconstruct line
                    line = before + clean_content + after
            
            elif "print(f'" in line:
                # Handle f-string prints
                line = re.sub(r'[🚀📊🔍✅❌🧪📝🎯🔧📁💾🏠📦📈🔥⚡💡🎉🚨📋🤖⏱️📤🔄💾🗂️🛠️🗄️📚💻🎯🎭🏗️🔮📞📄🔍🎨📊🏆🤝📝📍📈🎯📱💼📚🔧⚙️🎛️📏🗃️📐📊⚡🎵🎨💫🌟⭐✨🎪🔤🤷‍♂️🔥💡✨] ', '', line)
        
        elif line.strip().startswith('#'):
            # Handle comments
            line = re.sub(r'[🚀📊🔍✅❌🧪📝🎯🔧📁💾🏠📦📈🔥⚡💡🎉🚨📋🤖⏱️📤🔄💾🗂️🛠️🗄️📚💻🎯🎭🏗️🔮📞📄🔍🎨📊🏆🤝📝📍📈🎯📱💼📚🔧⚙️🎛️📏🗃️📐📊⚡🎵🎨💫🌟⭐✨🎪🔤🤷‍♂️🔥💡✨] ', '', line)
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def safe_clean_file(file_path: Path) -> bool:
    """Safely clean emojis from a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Check if original is valid
        if not is_valid_python(original_content):
            print(f"Skipping invalid Python file: {file_path}")
            return False
        
        cleaned_content = safe_clean_emojis(original_content)
        
        # Check if cleaned version is still valid
        if not is_valid_python(cleaned_content):
            print(f"Cleaning would break syntax, skipping: {file_path}")
            return False
        
        # Only write if there are changes and it's still valid
        if cleaned_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"Safely cleaned: {file_path}")
            return True
        else:
            print(f"No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to safely clean all Python files"""
    project_root = Path(__file__).parent.parent
    
    # Find all Python files (excluding .venv and problematic files)
    python_files = []
    exclude_patterns = ['.venv', '__pycache__', 'build', 'dist']
    
    for file_path in project_root.rglob('*.py'):
        if not any(pattern in str(file_path) for pattern in exclude_patterns):
            python_files.append(file_path)
    
    print(f"Found {len(python_files)} Python files to process")
    
    cleaned_count = 0
    for file_path in python_files:
        if safe_clean_file(file_path):
            cleaned_count += 1
    
    print(f"\nSafe cleaning complete!")
    print(f"Files processed: {len(python_files)}")
    print(f"Files modified: {cleaned_count}")
    print(f"Files unchanged: {len(python_files) - cleaned_count}")

if __name__ == "__main__":
    main()


