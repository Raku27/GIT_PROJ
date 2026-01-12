# Example Usage Guide

This guide provides examples for using each project in the portfolio.

## Quick Start

Each project includes an `example_usage.py` script that demonstrates the core functionality.

### 1. Data Hotel Analysis with PowerBI

```bash
cd 01-data-hotel-analysis-powerbi
python example_usage.py
```

**Key Features:**
- Data cleaning and preprocessing
- Feature transformation for PowerBI
- Data validation and quality checks

### 2. Matching Project

```bash
cd 02-matching-project
python example_usage.py
```

**Key Features:**
- Hungarian algorithm for optimal matching
- Gale-Shapley algorithm for stable matching
- REST API for matching service

**Start API Server:**
```bash
python -m src.api.main
# API available at http://localhost:8000
```

### 3. Engineering Pipeline Agent

```bash
cd 03-engineering-pipeline-agent
python example_usage.py
```

**Key Features:**
- Intelligent pipeline orchestration
- CI/CD pipeline configurations
- Automated deployment scripts

### 4. AI Analysis

```bash
cd 04-ai-analysis
python example_usage.py
```

**Key Features:**
- Machine learning model training
- Feature engineering
- Model inference and predictions

## Installation

Each project has its own `requirements.txt`. Install dependencies:

```bash
# For each project
pip install -r requirements.txt
```

## Project-Specific Examples

### Data Hotel Analysis

```python
from scripts.data_cleaning import HotelDataCleaner

cleaner = HotelDataCleaner('data/raw/hotel_bookings.csv')
cleaned_df = cleaner.clean_data(date_columns=['check_in_date', 'check_out_date'])
cleaner.save_cleaned_data('data/processed/hotel_bookings_cleaned.csv')
```

### Matching Project

```python
from src.algorithms.hungarian import HungarianMatcher
from src.models.entities import Entity, EntityType, Criteria

matcher = HungarianMatcher()
result = matcher.match(entities_a, entities_b, criteria)
print(f"Found {len(result.matches)} matches")
```

### Engineering Pipeline

```python
from agents.orchestrator_agent import OrchestratorAgent

orchestrator = OrchestratorAgent(config)
result = orchestrator.execute_pipeline(project_config)
```

### AI Analysis

```python
from src.models.classifier import MLClassifier

classifier = MLClassifier(algorithm='random_forest')
results = classifier.train(X, y)
predictions = classifier.predict(X_test)
```

## API Usage

### Matching Service API

```bash
# Start server
python -m src.api.main

# Make request
curl -X POST http://localhost:8000/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "entities_a": [...],
    "entities_b": [...],
    "criteria": {...},
    "algorithm": "hungarian"
  }'
```

## Next Steps

1. **Add Your Data**: Replace example data with your actual datasets
2. **Customize**: Modify configurations and parameters for your use case
3. **Extend**: Add new features and functionality
4. **Deploy**: Deploy to production environments

For detailed documentation, see each project's README.md file.
