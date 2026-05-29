# Text2SQL RAG System

Professional Text-to-SQL system using Retrieval-Augmented Generation (RAG) for converting natural language questions to SQL queries.

## Features

- **Question Type Classification** - Automatic question type analysis
- **Multi-LLM Support** - Support for Typhoon, OpenAI, Claude, Gemini
- **Multi-Embedding Models** - Support for multiple embedding models
- **Comprehensive Evaluation** - Standard metrics evaluation
- **Post-Processing** - Automatic SQL improvement
- **Batch Processing** - Process multiple questions simultaneously

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd text2sql_rag
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Create a `.env` file in the root directory:
```env
# LLM API Keys
TYPHOON_API_KEY=your_typhoon_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key

# Hugging Face
HUGGINGFACE_API_KEY=your_huggingface_api_key
```

### 4. Initialize Database
```bash
make setup-data
```

## Usage

### Command Line Interface

**Single Question:**
```bash
python main.py -q "Show patient count by hospital"
```

**Interactive Mode:**
```bash
python main.py -i
```

**Batch Processing:**
```bash
python main.py -f questions.json -o results.json
```

**Custom Schema:**
```bash
python main.py -q "Your question" -s "Your schema"
```

### Python API

```python
from text2sql_rag import Text2SQLRAGSystem

# Initialize system
system = Text2SQLRAGSystem()

# Process single question
result = system.process_question("Show all patients")
print(result['generated_sql'])

# Batch processing
questions = ["Question 1", "Question 2"]
results = system.batch_process(questions)
```

## Testing

### Unit Tests
```bash
make test-unit
```

### Integration Tests
```bash
make test-integration
```

### Performance Benchmarks
```bash
make test-benchmarks
```

### All Tests
```bash
make test
```

## Evaluation

### Simple Evaluation
```bash
make eval-simple
```

### Comprehensive Evaluation
```bash
make eval
```

## Development

### Code Quality
```bash
make format        # Format code
make lint         # Check code quality
make beautify     # Remove emojis and beautify
make clean-code   # Full code cleanup
```

### Project Structure

```
text2sql_rag/
├── src/                    # Source code
│   └── text2sql_rag/      # Main package
├── tests/                 # Test files
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── benchmarks/       # Performance tests
├── results/              # Experiment results
├── data/                 # Data files
├── configs/              # Configuration files
├── scripts/              # Utility scripts
└── docs/                 # Documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Submit a pull request

## License

MIT License