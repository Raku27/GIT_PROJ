"""
Example usage script for Matching Project
Demonstrates how to use the matching algorithms
"""

from src.models.entities import Entity, EntityType, Criteria
from src.algorithms.hungarian import HungarianMatcher
from src.algorithms.gale_shapley import GaleShapleyMatcher

def create_example_entities():
    """Create example entities for matching"""
    
    # Example: Job candidates and job positions
    candidates = [
        Entity(
            id="candidate_1",
            entity_type=EntityType.CANDIDATE,
            attributes={
                "experience_years": 5,
                "skills": ["Python", "Machine Learning", "Data Science"],
                "education": "Master's",
                "location": "San Francisco"
            },
            preferences=["job_1", "job_2", "job_3"]
        ),
        Entity(
            id="candidate_2",
            entity_type=EntityType.CANDIDATE,
            attributes={
                "experience_years": 3,
                "skills": ["Java", "Spring", "Microservices"],
                "education": "Bachelor's",
                "location": "New York"
            },
            preferences=["job_2", "job_1", "job_3"]
        ),
        Entity(
            id="candidate_3",
            entity_type=EntityType.CANDIDATE,
            attributes={
                "experience_years": 7,
                "skills": ["Python", "Django", "PostgreSQL"],
                "education": "Master's",
                "location": "Remote"
            },
            preferences=["job_1", "job_3", "job_2"]
        )
    ]
    
    jobs = [
        Entity(
            id="job_1",
            entity_type=EntityType.JOB,
            attributes={
                "required_skills": ["Python", "Machine Learning"],
                "min_experience": 3,
                "education_level": "Bachelor's",
                "location": "San Francisco"
            },
            preferences=["candidate_1", "candidate_3", "candidate_2"]
        ),
        Entity(
            id="job_2",
            entity_type=EntityType.JOB,
            attributes={
                "required_skills": ["Java", "Spring"],
                "min_experience": 2,
                "education_level": "Bachelor's",
                "location": "New York"
            },
            preferences=["candidate_2", "candidate_1", "candidate_3"]
        ),
        Entity(
            id="job_3",
            entity_type=EntityType.JOB,
            attributes={
                "required_skills": ["Python", "Django"],
                "min_experience": 5,
                "education_level": "Master's",
                "location": "Remote"
            },
            preferences=["candidate_3", "candidate_1", "candidate_2"]
        )
    ]
    
    return candidates, jobs

def main():
    """Example matching workflow"""
    
    print("=" * 60)
    print("Matching Project - Example Usage")
    print("=" * 60)
    
    # Create example entities
    candidates, jobs = create_example_entities()
    
    # Define matching criteria
    criteria = Criteria(
        weights={
            "experience_years": 0.3,
            "skills": 0.4,
            "education": 0.2,
            "location": 0.1
        },
        required_attributes=["experience_years", "skills"],
        optional_attributes=["education", "location"],
        min_score=0.5,
        max_matches=1
    )
    
    # Test Hungarian Algorithm
    print("\n1. Hungarian Algorithm (Optimal Matching)")
    print("-" * 60)
    hungarian_matcher = HungarianMatcher()
    result_hungarian = hungarian_matcher.match(candidates, jobs, criteria)
    
    print(f"Matches found: {len(result_hungarian.matches)}")
    for match in result_hungarian.matches:
        print(f"  {match.entity_a_id} <-> {match.entity_b_id} (score: {match.score:.2f})")
    
    print(f"\nUnmatched: {result_hungarian.unmatched_entities}")
    print(f"Total Score: {result_hungarian.total_score:.2f}")
    print(f"Execution Time: {result_hungarian.execution_time:.4f}s")
    
    # Test Gale-Shapley Algorithm
    print("\n2. Gale-Shapley Algorithm (Stable Matching)")
    print("-" * 60)
    gs_matcher = GaleShapleyMatcher()
    result_gs = gs_matcher.match(candidates, jobs, criteria)
    
    print(f"Matches found: {len(result_gs.matches)}")
    for match in result_gs.matches:
        print(f"  {match.entity_a_id} <-> {match.entity_b_id} (score: {match.score:.2f})")
    
    print(f"\nUnmatched: {result_gs.unmatched_entities}")
    print(f"Total Score: {result_gs.total_score:.2f}")
    print(f"Execution Time: {result_gs.execution_time:.4f}s")
    
    # Statistics
    print("\n3. Matching Statistics")
    print("-" * 60)
    stats_h = result_hungarian.get_statistics()
    stats_gs = result_gs.get_statistics()
    
    print("Hungarian Algorithm:")
    for key, value in stats_h.items():
        print(f"  {key}: {value}")
    
    print("\nGale-Shapley Algorithm:")
    for key, value in stats_gs.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("To use the API:")
    print("1. Start the API server: python -m src.api.main")
    print("2. Send POST requests to http://localhost:8000/api/match")
    print("=" * 60)

if __name__ == "__main__":
    main()
