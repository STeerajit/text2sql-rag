#!/usr/bin/env python3
"""
Script to clean emojis from README and documentation files
"""

import re
from pathlib import Path

def clean_markdown_file(file_path: Path) -> bool:
    """Clean emojis from markdown files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove emojis from headers and content
        emoji_pattern = re.compile(
            r'[🚀📊🔍✅❌🧪📝🎯🔧📁💾🏠📦📈🔥⚡💡🎉🚨📋🤖⏱️📤🔄💾🗂️🛠️🗄️📚💻'
            r'🎯🎭🏗️🔮📞📄🔍🎨📊🏆🤝📝📍📈🎯📱💼📚🔧⚙️🎛️📏🗃️📐📊⚡🎵🎨💫🌟⭐✨🎪🔤🤷‍♂️🔥💡✨]'
        )
        
        # Remove emojis
        content = emoji_pattern.sub('', content)
        
        # Clean up specific patterns
        replacements = [
            # Headers
            (r'# Text2SQL RAG System 🚀', '# Text2SQL RAG System'),
            (r'## ✨ คุณสมบัติหลัก', '## คุณสมบัติหลัก'),
            (r'## 🚀 การติดตั้ง', '## การติดตั้ง'),
            (r'## 📋 การใช้งาน', '## การใช้งาน'),
            (r'## 🧪 การทดสอบ', '## การทดสอบ'),
            (r'## 📊 ผลการประเมิน', '## ผลการประเมิน'),
            (r'## 🔧 การพัฒนา', '## การพัฒนา'),
            (r'## 📁 โครงสร้างโปรเจค', '## โครงสร้างโปรเจค'),
            (r'## 🤝 การมีส่วนร่วม', '## การมีส่วนร่วม'),
            (r'## 📄 ใบอนุญาต', '## ใบอนุญาต'),
            
            # List items - remove leading emojis but keep content
            (r'- 🔍 \*\*(.+?)\*\* - (.+)', r'- **\1** - \2'),
            (r'- 🤖 \*\*(.+?)\*\* - (.+)', r'- **\1** - \2'),
            (r'- 🔤 \*\*(.+?)\*\* - (.+)', r'- **\1** - \2'),
            (r'- 📊 \*\*(.+?)\*\* - (.+)', r'- **\1** - \2'),
            (r'- 🎯 \*\*(.+?)\*\* - (.+)', r'- **\1** - \2'),
            (r'- 📁 \*\*(.+?)\*\* - (.+)', r'- **\1** - \2'),
            
            # Subsection headers
            (r'### 🔧 (.+)', r'### \1'),
            (r'### 📝 (.+)', r'### \1'),
            (r'### 🚀 (.+)', r'### \1'),
            (r'### ✅ (.+)', r'### \1'),
            (r'### 📊 (.+)', r'### \1'),
            (r'### 🧪 (.+)', r'### \1'),
            
            # Clean up multiple spaces
            (r'\s{2,}', ' '),
            
            # Clean up empty lines with just spaces
            (r'^\s+$', '', re.MULTILINE),
        ]
        
        for pattern, replacement, *flags in replacements:
            if flags:
                content = re.sub(pattern, replacement, content, flags=flags[0])
            else:
                content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Cleaned: {file_path}")
            return True
        else:
            print(f"No changes: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to clean documentation files"""
    project_root = Path(__file__).parent.parent
    
    # Find all markdown files
    md_files = []
    for pattern in ['*.md', '**/*.md']:
        for file_path in project_root.glob(pattern):
            if '.venv' not in str(file_path):
                md_files.append(file_path)
    
    print(f"Found {len(md_files)} markdown files to clean")
    
    cleaned_count = 0
    for file_path in md_files:
        if clean_markdown_file(file_path):
            cleaned_count += 1
    
    print(f"\nCleaning complete!")
    print(f"Files processed: {len(md_files)}")
    print(f"Files modified: {cleaned_count}")
    print(f"Files unchanged: {len(md_files) - cleaned_count}")

if __name__ == "__main__":
    main()


