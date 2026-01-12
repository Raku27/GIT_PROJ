"""
FastAPI application for matching service
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn

from ..models.entities import Entity, EntityType, Criteria, Match
from ..algorithms.hungarian import HungarianMatcher
from ..algorithms.gale_shapley import GaleShapleyMatcher

app = FastAPI(
    title="Matching Service API",
    description="API for intelligent entity matching",
    version="1.0.0"
)


class EntityRequest(BaseModel):
    """Entity request model"""
    id: str
    entity_type: str
    attributes: Dict[str, Any]
    preferences: Optional[List[str]] = None
    constraints: Optional[Dict[str, Any]] = None


class CriteriaRequest(BaseModel):
    """Criteria request model"""
    weights: Dict[str, float]
    required_attributes: List[str] = []
    optional_attributes: List[str] = []
    min_score: float = 0.0
    max_matches: int = 1


class MatchingRequest(BaseModel):
    """Matching request model"""
    entities_a: List[EntityRequest]
    entities_b: List[EntityRequest]
    criteria: CriteriaRequest
    algorithm: str = "hungarian"  # "hungarian" or "gale_shapley"


class MatchResponse(BaseModel):
    """Match response model"""
    entity_a_id: str
    entity_b_id: str
    score: float
    details: Dict[str, Any]


class MatchingResponse(BaseModel):
    """Matching response model"""
    matches: List[MatchResponse]
    unmatched_entities: List[str]
    total_score: float
    execution_time: float
    statistics: Dict[str, Any]


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Matching Service API",
        "version": "1.0.0",
        "endpoints": {
            "match": "/api/match",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/match", response_model=MatchingResponse)
async def match_entities(request: MatchingRequest):
    """
    Perform matching between two sets of entities
    
    Args:
        request: Matching request with entities and criteria
        
    Returns:
        Matching result with matches and statistics
    """
    try:
        # Convert request entities to Entity objects
        entities_a = [
            Entity(
                id=e.id,
                entity_type=EntityType(e.entity_type),
                attributes=e.attributes,
                preferences=e.preferences,
                constraints=e.constraints
            )
            for e in request.entities_a
        ]
        
        entities_b = [
            Entity(
                id=e.id,
                entity_type=EntityType(e.entity_type),
                attributes=e.attributes,
                preferences=e.preferences,
                constraints=e.constraints
            )
            for e in request.entities_b
        ]
        
        # Convert criteria
        criteria = Criteria(
            weights=request.criteria.weights,
            required_attributes=request.criteria.required_attributes,
            optional_attributes=request.criteria.optional_attributes,
            min_score=request.criteria.min_score,
            max_matches=request.criteria.max_matches
        )
        
        # Select algorithm
        if request.algorithm.lower() == "hungarian":
            matcher = HungarianMatcher()
        elif request.algorithm.lower() == "gale_shapley":
            matcher = GaleShapleyMatcher()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown algorithm: {request.algorithm}")
        
        # Perform matching
        result = matcher.match(entities_a, entities_b, criteria)
        
        # Convert to response format
        match_responses = [
            MatchResponse(
                entity_a_id=m.entity_a_id,
                entity_b_id=m.entity_b_id,
                score=m.score,
                details=m.details
            )
            for m in result.matches
        ]
        
        return MatchingResponse(
            matches=match_responses,
            unmatched_entities=result.unmatched_entities,
            total_score=result.total_score,
            execution_time=result.execution_time,
            statistics=result.get_statistics()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
