"""Bounded matching API. Synchronous endpoints run outside the ASGI event loop."""

import json
import logging
from typing import Any, Literal
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..algorithms.gale_shapley import GaleShapleyMatcher
from ..algorithms.hungarian import HungarianMatcher
from ..models.entities import Criteria, Entity, EntityType

logger = logging.getLogger(__name__)
app = FastAPI(title="Matching Service API", version="1.1.0")


@app.exception_handler(RequestValidationError)
def validation_error_handler(request, exc):
    # Omit raw input and error context: these can contain secrets or nonfinite numbers.
    errors = [
        {"loc": error["loc"], "msg": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})


class RequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class EntityRequest(RequestModel):
    id: str = Field(min_length=1, max_length=128)
    entity_type: EntityType
    attributes: dict[str, Any] = Field(max_length=50)
    preferences: list[str] | None = Field(default=None, max_length=200)
    constraints: dict[str, Any] | None = None

    @model_validator(mode="after")
    def bounded_attributes(self):
        try:
            size = len(json.dumps(self.attributes, allow_nan=False).encode())
        except (ValueError, TypeError) as exc:
            raise ValueError("Attributes must be finite JSON values") from exc
        if size > 10000:
            raise ValueError("Attributes must fit within 10000 JSON bytes")
        return self


class CriteriaRequest(RequestModel):
    weights: dict[str, float] = Field(min_length=1, max_length=50)
    required_attributes: list[str] = Field(default_factory=list, max_length=50)
    optional_attributes: list[str] = Field(default_factory=list, max_length=50)
    min_score: float = Field(default=0.0, ge=0, le=1)
    max_matches: Literal[1] = 1
    attribute_mappings: dict[str, str] = Field(default_factory=dict, max_length=50)

    @model_validator(mode="after")
    def valid_weights(self):
        Criteria(**self.model_dump())
        return self


class MatchingRequest(RequestModel):
    entities_a: list[EntityRequest] = Field(max_length=200)
    entities_b: list[EntityRequest] = Field(max_length=200)
    criteria: CriteriaRequest
    algorithm: Literal["hungarian", "gale_shapley"] = "hungarian"


class MatchResponse(BaseModel):
    entity_a_id: str
    entity_b_id: str
    score: float
    details: dict[str, Any]


class MatchingResponse(BaseModel):
    matches: list[MatchResponse]
    unmatched_entities: list[str]
    total_score: float
    execution_time: float
    statistics: dict[str, Any]


@app.get("/")
def root():
    return {
        "message": "Matching Service API",
        "version": "1.1.0",
        "endpoints": {"match": "/api/match", "health": "/health"},
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/api/match", response_model=MatchingResponse)
def match_entities(request: MatchingRequest):
    try:
        a = [Entity(**e.model_dump()) for e in request.entities_a]
        b = [Entity(**e.model_dump()) for e in request.entities_b]
        criteria = Criteria(**request.criteria.model_dump())
        matcher = (
            HungarianMatcher()
            if request.algorithm == "hungarian"
            else GaleShapleyMatcher()
        )
        result = matcher.match(a, b, criteria)
        return {
            "matches": [vars(m) for m in result.matches],
            "unmatched_entities": result.unmatched_entities,
            "total_score": result.total_score,
            "execution_time": result.execution_time,
            "statistics": result.get_statistics(),
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        request_id = uuid4().hex
        logger.exception("Matching request failed: %s", request_id)
        raise HTTPException(
            status_code=500,
            detail={"message": "Matching failed", "request_id": request_id},
        ) from exc


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
