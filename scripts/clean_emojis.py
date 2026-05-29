#!/usr/bin/env python3
"""
Script to remove emojis from all Python files in the project
Simple and safe implementation
"""

import os
import re
from pathlib import Path

def clean_emoji_from_text(text: str) -> str:
    """Remove emojis from text safely"""
    # Simple emoji removal
    emoji_pattern = re.compile(r'[🚀📊🔍✅❌🧪📝🎯🔧📁💾🏠📦📈🔥⚡💡🎉🚨📋🤖⏱️]')
    text = emoji_pattern.sub('', text)
    
    # Clean up multiple spaces
    text = re.sub(r'\s{2,}', ' ', text)
    
    return text

def clean_file(file_path: Path) -> bool:
    """Clean emojis from a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        cleaned_content = clean_emoji_from_text(content)
        
        if cleaned_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"Cleaned: {file_path}")
            return True
        else:
            print(f"No changes: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to clean all Python files"""
    project_root = Path(__file__).parent.parent
    
    # Find Python files (excluding .venv)
    python_files = []
    for pattern in ['**/*.py']:
        for file_path in project_root.glob(pattern):
            if '.venv' not in str(file_path) and '__pycache__' not in str(file_path):
                python_files.append(file_path)
    
    print(f"Found {len(python_files)} Python files to process")
    
    cleaned_count = 0
    for file_path in python_files:
        if clean_file(file_path):
            cleaned_count += 1
    
    print(f"\nProcessing complete!")
    print(f"Files processed: {len(python_files)}")
    print(f"Files modified: {cleaned_count}")
    print(f"Files unchanged: {len(python_files) - cleaned_count}")

if __name__ == "__main__":
    main()