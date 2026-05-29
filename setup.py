# !/usr/bin/env python3
"""
Setup script for Text2SQL RAG System
""" from setuptools import setup, find_packages
import os # Read README file
with open("README.md", "r", encoding="utf-8") as fh: long_description = fh.read() # Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh: requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")] setup( name="text2sql-rag", version="1.0.0", author="Text2SQL RAG Team", description="ระบบแปลงคำถามภาษาไทยเป็น SQL ด้วย Retrieval-Augmented Generation", long_description=long_description, long_description_content_type="text/markdown", url="https://github.com/your-repo/text2sql-rag", package_dir={"": "src"}, packages=find_packages(where="src"), classifiers=[ "Development Status :: 4 - Beta", "Intended Audience :: Developers", "License :: OSI Approved :: MIT License", "Operating System :: OS Independent", "Programming Language :: Python :: 3", "Programming Language :: Python :: 3.8", "Programming Language :: Python :: 3.9", "Programming Language :: Python :: 3.10", "Programming Language :: Python :: 3.11", "Topic :: Software Development :: Libraries :: Python Modules", "Topic :: Scientific/Engineering :: Artificial Intelligence", "Topic :: Database", ], python_requires=">=3.8", install_requires=requirements, extras_require={ "dev": [ "pytest>=7.0.0", "pytest-cov>=4.0.0", "black>=22.0.0", "flake8>=5.0.0", "mypy>=0.991", ], }, entry_points={ "console_scripts": [ "text2sql=text2sql_rag.main:main", ], }, include_package_data=True, package_data={ "text2sql_rag": ["*.json", "*.txt"], }, zip_safe=False,
)


