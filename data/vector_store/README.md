# Vector Store Organization This directory contains all vector databases used by the Text2SQL RAG system. ## Directory Structure ```
vector_store/
├── main/ # Production vector stores
│ ├── production_chroma.sqlite3 # Main ChromaDB database
│ └── 849001e5-efc5-4d11-a041-b3aacadbb156/ # Main collection data
├── experiments/ # Experimental vector stores
│ ├── test_chroma.sqlite3 # Test ChromaDB database
│ ├── 34771bc1-ed95-417a-9662-9f40dc568b1e/ # Experiment collection 1
│ └── ef5130a7-fb9e-4872-af3d-f8e2ac2236d3/ # Experiment collection 2
└── archive/ # Archived/backup vector stores
``` ## Vector Store Types ### Main Vector Stores
- **production_chroma.sqlite3**: Primary ChromaDB database for production use
- **849001e5-efc5-4d11-a041-b3aacadbb156/**: Main collection containing schema embeddings ### Experimental Vector Stores
- **test_chroma.sqlite3**: Used for testing and development
- **34771bc1-ed95-417a-9662-9f40dc568b1e/**: Experimental embeddings (likely different models)
- **ef5130a7-fb9e-4872-af3d-f8e2ac2236d3/**: Another experimental setup ## Usage ### Creating New Vector Store
```bash
python text2sql_rag/init_vector.py
``` ### Using Specific Vector Store
The system automatically uses the main vector store located in `main/production_chroma.sqlite3`. ### Testing with Different Vector Stores
For testing, you can temporarily copy files from `experiments/` to `main/` or modify the vector store path in configuration. ## 🧹 Maintenance ### Cleaning Up
- Move old experimental vector stores to `archive/`
- Remove unused collections periodically
- Keep only the most recent and effective embeddings ### Backup
- Regularly backup `main/` directory
- Keep snapshots of successful experimental setups in `archive/` ## Collection Information Each UUID-named directory contains:
- `data_level0.bin`: Vector data
- `header.bin`: Metadata headers
- `length.bin`: Length information
- `link_lists.bin`: Graph connectivity data These are ChromaDB's internal storage format for HNSW (Hierarchical Navigable Small World) index.


