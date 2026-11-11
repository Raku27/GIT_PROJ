"""Domain objects and validated matching criteria."""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EntityType(str, Enum):
    USER = "user"
    ITEM = "item"
    JOB = "job"
    CANDIDATE = "candidate"
    MENTOR = "mentor"
    MENTEE = "mentee"


@dataclass
class Entity:
    id: str
    entity_type: EntityType
    attributes: dict[str, Any]
    preferences: list[str] | None = None
    constraints: dict[str, Any] | None = None

    def get_attribute(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)

    def has_preference(self, entity_id: str) -> bool:
        return entity_id in (self.preferences or [])


@dataclass
class Criteria:
    weights: dict[str, float]
    required_attributes: list[str] = field(default_factory=list)
    optional_attributes: list[str] = field(default_factory=list)
    min_score: float = 0.0
    max_matches: int = 1
    attribute_mappings: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.weights or any(
            not math.isfinite(v) or v < 0 for v in self.weights.values()
        ):
            raise ValueError(
                "Weights must be finite, nonnegative and have a positive sum"
            )
        total = sum(self.weights.values())
        if not math.isfinite(total) or total <= 0:
            raise ValueError("Weights must have a finite positive sum")
        if not math.isfinite(self.min_score) or not 0 <= self.min_score <= 1:
            raise ValueError("min_score must be between 0 and 1")
        if self.max_matches != 1:
            raise ValueError("Only one-to-one matching (max_matches=1) is supported")
        self.weights = {k: v / total for k, v in self.weights.items()}

    def calculate_weighted_score(self, scores: dict[str, float]) -> float:
        return sum(self.weights.get(k, 0) * v for k, v in scores.items())


@dataclass
class Match:
    entity_a_id: str
    entity_b_id: str
    score: float
    details: dict[str, Any]
    matched_at: str | None = None


@dataclass
class MatchingResult:
    matches: list[Match]
    unmatched_entities: list[str]
    total_score: float
    execution_time: float

    def get_match_for_entity(self, entity_id: str) -> Match | None:
        return next(
            (m for m in self.matches if entity_id in (m.entity_a_id, m.entity_b_id)),
            None,
        )

    def get_statistics(self) -> dict[str, Any]:
        return {
            "total_matches": len(self.matches),
            "unmatched_count": len(self.unmatched_entities),
            "average_score": self.total_score / len(self.matches)
            if self.matches
            else 0,
            "total_score": self.total_score,
            "execution_time_seconds": self.execution_time,
        }
