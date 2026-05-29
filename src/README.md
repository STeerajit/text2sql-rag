# Source Code This directory contains the main source code for the Text2SQL RAG system. ## Structure ```
src/
└── text2sql_rag/ # Core package ├── main.py # Main application entry point ├── ultimate_prompt.py # Ultimate prompt system ├── enhanced_prompt.py # Enhanced prompt system ├── llm.py # LLM integration ├── embedding.py # Embedding models ├── text2sql_knowledge.py # Knowledge base ├── auto_corrector.py # SQL auto-correction ├── retrieval.py # RAG retrieval system ├── init_vector.py # Vector store initialization ├── init_db.py # Database initialization ├── cli.py # Command line interface ├── prompt.py # Basic prompt system └── run_query.py # SQL execution utilities
``` ## Usage The main application can be run from the root directory: ```bash
python main.py -i # Interactive mode
``` ## Development For development, install the package in editable mode: ```bash
pip install -e .
```


