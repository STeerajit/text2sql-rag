# Test Suite This directory contains all test files organized by type. ## Structure ```
tests/
├── unit/ # Unit tests
│ ├── simple_comprehensive_test.py
│ ├── simple_test_cases.py
│ └── simple_evaluator.py
├── integration/ # Integration tests
│ ├── comprehensive_evaluation.py
│ ├── comprehensive_test_cases.py
│ ├── comprehensive_llm_test.py
│ └── enhanced_evaluator.py
├── benchmarks/ # Performance benchmarks
│ ├── performance_test.py
│ ├── detailed_performance_test.py
│ └── performance_benchmark.py
└── legacy/ # Legacy test files
``` ## Test Types ### Unit Tests (`unit/`)
- Test individual components in isolation
- Fast execution
- Basic functionality verification ### Integration Tests (`integration/`)
- Test component interactions
- End-to-end functionality
- System-level testing ### Benchmarks (`benchmarks/`)
- Performance measurements
- Memory usage tests
- Execution time analysis ## Running Tests ### All Tests
```bash
make test
``` ### Unit Tests Only
```bash
python tests/unit/simple_comprehensive_test.py
``` ### Integration Tests
```bash
python tests/integration/comprehensive_evaluation.py
``` ### Benchmarks
```bash
python tests/benchmarks/performance_test.py
``` ## Test Results Test results are automatically saved to the `results/` directory:
- Unit test results → `results/evaluation/`
- Integration results → `results/comprehensive/`
- Benchmark results → `results/performance/` ## Adding New Tests 1. Choose appropriate category (unit/integration/benchmarks)
2. Follow naming convention: `test_*.py` or `*_test.py`
3. Include proper documentation and examples
4. Update this README if adding new test types


