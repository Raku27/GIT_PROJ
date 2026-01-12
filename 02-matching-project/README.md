# Matching Project

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Algorithm](https://img.shields.io/badge/Algorithm-Optimization-green.svg)]()

## 📋 Overview

An intelligent matching system designed to pair entities (users, items, jobs, candidates, etc.) based on multiple criteria and constraints. This project demonstrates advanced algorithm design, optimization techniques, and scalable system architecture for matching problems.

## ✨ Features

- **Multi-Criteria Matching**: Match entities based on multiple weighted criteria
- **Optimization Algorithms**: Implement various matching algorithms (Hungarian, Gale-Shapley, Greedy, etc.)
- **Constraint Handling**: Support for hard and soft constraints
- **Scalability**: Efficient algorithms for large-scale matching problems
- **Performance Metrics**: Comprehensive evaluation and benchmarking
- **API Interface**: RESTful API for integration with other systems
- **Visualization**: Interactive dashboards for matching results

## 🎯 Use Cases

- Job candidate matching
- Mentor-mentee pairing
- Product recommendation
- Resource allocation
- Team formation
- Dating/matchmaking applications
- Course-student assignment

## 🛠️ Technologies Used

- **Python**: Core implementation language
- **FastAPI**: RESTful API framework for matching service
- **Algorithms**: Graph algorithms, optimization, linear programming
- **Libraries**: NumPy, SciPy, NetworkX, Pandas
- **Uvicorn**: ASGI server for FastAPI
- **Pydantic**: Data validation and settings management
- **Testing**: pytest for unit testing

## 📁 Project Structure

```
02-matching-project/
├── src/                    # Source code
│   ├── algorithms/         # Matching algorithms
│   │   ├── hungarian.py
│   │   ├── gale_shapley.py
│   │   └── greedy.py
│   ├── models/             # Data models
│   ├── api/                # API endpoints
│   └── utils/              # Utility functions
├── tests/                  # Test files
│   ├── test_algorithms.py
│   └── test_api.py
├── data/                   # Sample data and datasets
├── docs/                   # Documentation
│   ├── algorithm_design.md
│   └── api_documentation.md
├── notebooks/              # Jupyter notebooks for analysis
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip package manager
- (Optional) PostgreSQL for database storage

### Installation

```bash
# Clone the repository
git clone https://github.com/Raku27/GIT_PROJ.git
cd GIT_PROJ/02-matching-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### Basic Matching

```python
from src.algorithms.hungarian import HungarianMatcher
from src.models.entities import Entity, Criteria

# Create entities and criteria
entities_a = [Entity(id=1, attributes={...}), ...]
entities_b = [Entity(id=2, attributes={...}), ...]

# Initialize matcher
matcher = HungarianMatcher()

# Perform matching
matches = matcher.match(entities_a, entities_b, criteria)
print(matches)
```

#### API Usage (FastAPI)

```bash
# Start the FastAPI server
python -m src.api.main
# Server runs at http://localhost:8000

# Interactive API documentation
# Visit: http://localhost:8000/docs (Swagger UI)
# Or: http://localhost:8000/redoc (ReDoc)

# Make matching request
curl -X POST http://localhost:8000/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "entities_a": [...],
    "entities_b": [...],
    "criteria": {...},
    "algorithm": "hungarian"
  }'
```

**📚 See detailed API guide**: `docs/api_usage_guide.md`

## 🔧 Algorithms Implemented

### 1. Hungarian Algorithm
- Optimal assignment for bipartite matching
- Time complexity: O(n³)
- Best for: One-to-one matching with cost minimization

### 2. Gale-Shapley Algorithm
- Stable matching algorithm
- Time complexity: O(n²)
- Best for: Stable marriage problem, preference-based matching

### 3. Greedy Matching
- Fast heuristic approach
- Time complexity: O(n log n)
- Best for: Large-scale approximate matching

### 4. Linear Programming
- Optimal solution using optimization
- Best for: Complex constraints and multi-objective optimization

## 📊 Performance Metrics

- **Matching Quality**: Satisfaction score, preference fulfillment
- **Algorithm Efficiency**: Time complexity, execution time
- **Scalability**: Performance with increasing dataset size
- **Accuracy**: Comparison with optimal solutions

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_algorithms.py
```

## 📈 Example Results

*(Add example matching results and visualizations here)*

## 🔍 Algorithm Selection Guide

| Algorithm | Best For | Complexity | Optimal |
|-----------|----------|------------|---------|
| Hungarian | Cost minimization | O(n³) | Yes |
| Gale-Shapley | Stable matching | O(n²) | Yes |
| Greedy | Fast approximation | O(n log n) | No |
| Linear Programming | Complex constraints | Variable | Yes |

## 📚 Documentation

- [Algorithm Design](docs/algorithm_design.md) - Detailed algorithm explanations
- [API Documentation](docs/api_documentation.md) - API endpoints and usage
- [Performance Analysis](docs/performance.md) - Benchmarking results

## 🤝 Contributing

Contributions are welcome! Please read the [Contributing Guidelines](../../CONTRIBUTING.md) first.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## 👤 Author

**Rahul Kumaar Subramani**
- GitHub: [@Raku27](https://github.com/Raku27)
- Email: rahulkumaar27@gmail.com

---

⭐ If you found this project helpful, please give it a star!
