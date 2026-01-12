# FastAPI Matching Service - Usage Guide

## 🚀 Quick Start

The Matching Project includes a **FastAPI REST API** for intelligent entity matching. This guide shows you how to use it.

## Installation

```bash
cd 02-matching-project
pip install -r requirements.txt
```

## Starting the API Server

### Option 1: Direct Python Execution

```bash
python -m src.api.main
```

### Option 2: Using Uvicorn Directly

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: **http://localhost:8000**

## API Endpoints

### 1. Root Endpoint

**GET** `/`

Returns API information and available endpoints.

```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "message": "Matching Service API",
  "version": "1.0.0",
  "endpoints": {
    "match": "/api/match",
    "health": "/health"
  }
}
```

### 2. Health Check

**GET** `/health`

Check if the API is running.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

### 3. Matching Endpoint

**POST** `/api/match`

Perform matching between two sets of entities.

## Making Matching Requests

### Example Request (Job Matching)

```bash
curl -X POST http://localhost:8000/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "entities_a": [
      {
        "id": "candidate_1",
        "entity_type": "candidate",
        "attributes": {
          "experience_years": 5,
          "skills": ["Python", "Machine Learning"],
          "education": "Masters",
          "location": "San Francisco"
        },
        "preferences": ["job_1", "job_2"]
      },
      {
        "id": "candidate_2",
        "entity_type": "candidate",
        "attributes": {
          "experience_years": 3,
          "skills": ["Java", "Spring"],
          "education": "Bachelors",
          "location": "New York"
        },
        "preferences": ["job_2", "job_1"]
      }
    ],
    "entities_b": [
      {
        "id": "job_1",
        "entity_type": "job",
        "attributes": {
          "required_skills": ["Python", "Machine Learning"],
          "min_experience": 3,
          "location": "San Francisco"
        },
        "preferences": ["candidate_1", "candidate_2"]
      },
      {
        "id": "job_2",
        "entity_type": "job",
        "attributes": {
          "required_skills": ["Java", "Spring"],
          "min_experience": 2,
          "location": "New York"
        },
        "preferences": ["candidate_2", "candidate_1"]
      }
    ],
    "criteria": {
      "weights": {
        "experience_years": 0.3,
        "skills": 0.4,
        "education": 0.2,
        "location": 0.1
      },
      "required_attributes": ["experience_years", "skills"],
      "optional_attributes": ["education", "location"],
      "min_score": 0.5,
      "max_matches": 1
    },
    "algorithm": "hungarian"
  }'
```

### Example Response

```json
{
  "matches": [
    {
      "entity_a_id": "candidate_1",
      "entity_b_id": "job_1",
      "score": 0.85,
      "details": {
        "algorithm": "Hungarian Algorithm",
        "entity_a_type": "candidate",
        "entity_b_type": "job"
      }
    },
    {
      "entity_a_id": "candidate_2",
      "entity_b_id": "job_2",
      "score": 0.78,
      "details": {
        "algorithm": "Hungarian Algorithm",
        "entity_a_type": "candidate",
        "entity_b_type": "job"
      }
    }
  ],
  "unmatched_entities": [],
  "total_score": 1.63,
  "execution_time": 0.0023,
  "statistics": {
    "total_matches": 2,
    "unmatched_count": 0,
    "average_score": 0.815,
    "total_score": 1.63,
    "execution_time_seconds": 0.0023
  }
}
```

## Available Algorithms

### 1. Hungarian Algorithm

Optimal assignment for bipartite matching.

```json
{
  "algorithm": "hungarian"
}
```

**Best for:**
- Cost minimization
- One-to-one matching
- Optimal solutions

### 2. Gale-Shapley Algorithm

Stable matching algorithm.

```json
{
  "algorithm": "gale_shapley"
}
```

**Best for:**
- Stable matching
- Preference-based matching
- Stable marriage problem

## Request Format

### Entity Structure

```json
{
  "id": "unique_entity_id",
  "entity_type": "candidate|job|mentor|mentee|user|item",
  "attributes": {
    "key1": "value1",
    "key2": 123,
    "key3": ["list", "of", "values"]
  },
  "preferences": ["entity_id_1", "entity_id_2"],
  "constraints": {
    "constraint_key": "constraint_value"
  }
}
```

### Criteria Structure

```json
{
  "weights": {
    "attribute1": 0.4,
    "attribute2": 0.3,
    "attribute3": 0.3
  },
  "required_attributes": ["attribute1", "attribute2"],
  "optional_attributes": ["attribute3"],
  "min_score": 0.5,
  "max_matches": 1
}
```

**Note:** Weights should sum to approximately 1.0 (they'll be normalized automatically).

## Using Python Requests

### Example Python Script

```python
import requests
import json

# API endpoint
url = "http://localhost:8000/api/match"

# Prepare request data
data = {
    "entities_a": [
        {
            "id": "candidate_1",
            "entity_type": "candidate",
            "attributes": {
                "experience_years": 5,
                "skills": ["Python", "ML"],
                "education": "Masters"
            }
        }
    ],
    "entities_b": [
        {
            "id": "job_1",
            "entity_type": "job",
            "attributes": {
                "required_skills": ["Python", "ML"],
                "min_experience": 3
            }
        }
    ],
    "criteria": {
        "weights": {
            "experience_years": 0.3,
            "skills": 0.4,
            "education": 0.3
        },
        "required_attributes": ["experience_years"],
        "min_score": 0.5,
        "max_matches": 1
    },
    "algorithm": "hungarian"
}

# Make request
response = requests.post(url, json=data)

# Get results
result = response.json()
print(json.dumps(result, indent=2))
```

## Interactive API Documentation

FastAPI automatically generates interactive API documentation!

### Swagger UI

Visit: **http://localhost:8000/docs**

- Interactive API explorer
- Try out endpoints directly
- See request/response schemas
- Test different algorithms

### ReDoc

Visit: **http://localhost:8000/redoc**

- Alternative documentation format
- Clean, readable interface
- Complete API reference

## Error Handling

### 400 Bad Request

Invalid algorithm or malformed request:

```json
{
  "detail": "Unknown algorithm: invalid_algorithm"
}
```

### 500 Internal Server Error

Server error during matching:

```json
{
  "detail": "Error message describing the issue"
}
```

## Use Cases

### 1. Job-Candidate Matching

Match job seekers with job openings based on skills, experience, and preferences.

### 2. Mentor-Mentee Pairing

Pair mentors with mentees based on expertise, interests, and availability.

### 3. Product Recommendation

Match users with products based on preferences, ratings, and attributes.

### 4. Resource Allocation

Optimally allocate resources to tasks based on capabilities and constraints.

### 5. Team Formation

Form teams by matching team members based on skills and compatibility.

## Performance Tips

1. **Batch Processing**: Process multiple matching requests in batches
2. **Caching**: Cache frequently used criteria and entity sets
3. **Algorithm Selection**: Choose the right algorithm for your use case
4. **Data Preprocessing**: Clean and normalize data before sending to API

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Matching request (save request to file first)
curl -X POST http://localhost:8000/api/match \
  -H "Content-Type: application/json" \
  -d @request.json
```

### Using Python

```python
import requests

response = requests.get("http://localhost:8000/health")
print(response.json())
```

### Using Postman

1. Import the API endpoints
2. Create POST request to `/api/match`
3. Add JSON body with entities and criteria
4. Send request and view results

## Deployment

### Production Deployment

```bash
# Using Gunicorn with Uvicorn workers
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Run Examples**: Check `example_usage.py`
3. **Customize**: Modify algorithms or add new matching logic
4. **Integrate**: Connect to your applications

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **API Documentation**: http://localhost:8000/docs (when running)
- **Project README**: ../README.md

---

**Ready to start matching?** Run `python -m src.api.main` and visit http://localhost:8000/docs!
