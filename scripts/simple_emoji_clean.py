#!/usr/bin/env python3
"""
Simple and safe emoji cleaner
"""

import os
import re
from pathlib import Path

def clean_file_simple(file_path):
    """Simply remove emojis without complex replacements"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple emoji removal - just the most common ones
        emojis_to_remove = ['🚀', '📊', '🔍', '✅', '❌', '🧪', '📝', '🎯', '🔧', '📁', '💾']
        
        original = content
        for emoji in emojis_to_remove:
            content = content.replace(emoji + ' ', '')
            content = content.replace(emoji, '')
        
        # Only save if changed and still looks like valid Python
        if content != original and 'def ' in content and 'import ' in content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Cleaned: {file_path.name}")
            return True
        else:
            print(f"- Skipped: {file_path.name}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {file_path.name} - {e}")
        return False

def main():
    """Clean emojis safely"""
    print("🧹 Simple Emoji Cleaner")
    print("=" * 30)
    
    # Only process main source files
    files_to_clean = [
        'main.py',
        'src/text2sql_rag/ultimate_prompt.py',
        'src/text2sql_rag/llm.py',
        'src/text2sql_rag/embedding.py',
        'src/text2sql_rag/text2sql_knowledge.py'
    ]
    
    cleaned = 0
    for file_path in files_to_clean:
        path = Path(file_path)
        if path.exists():
            if clean_file_simple(path):
                cleaned += 1
    
    print(f"\n📈 Results: {cleaned} files cleaned")

if __name__ == "__main__":
    main()


