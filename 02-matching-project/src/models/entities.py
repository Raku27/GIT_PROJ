"""
Entity models for matching system
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum


class EntityType(Enum):
    """Types of entities that can be matched"""
    USER = "user"
    ITEM = "item"
    JOB = "job"
    CANDIDATE = "candidate"
    MENTOR = "mentor"
    MENTEE = "mentee"


@dataclass
class Entity:
    """Base entity class for matching"""
    id: str
    entity_type: EntityType
    attributes: Dict[str, Any]
    preferences: Optional[List[str]] = None
    constraints: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate entity after initialization"""
        if not self.attributes:
            self.attributes = {}
        if not self.preferences:
            self.preferences = []
        if not self.constraints:
            self.constraints = {}
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get attribute value"""
        return self.attributes.get(key, default)
    
    def has_preference(self, entity_id: str) -> bool:
        """Check if entity has preference for another entity"""
        return entity_id in self.preferences if self.preferences else False


@dataclass
class Criteria:
    """Matching criteria configuration"""
    weights: Dict[str, float]
    required_attributes: List[str]
    optional_attributes: List[str]
    min_score: float = 0.0
    max_matches: int = 1
    
    def __post_init__(self):
        """Validate criteria"""
        # Normalize weights to sum to 1
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            self.weights = {k: v / total_weight for k, v in self.weights.items()}
    
    def calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted score from individual attribute scores"""
        total_score = 0.0
        for attribute, score in scores.items():
            weight = self.weights.get(attribute, 0.0)
            total_score += weight * score
        return total_score


@dataclass
class Match:
    """Represents a match between two entities"""
    entity_a_id: str
    entity_b_id: str
    score: float
    details: Dict[str, Any]
    matched_at: Optional[str] = None
    
    def __repr__(self):
        return f"Match({self.entity_a_id} <-> {self.entity_b_id}, score={self.score:.2f})"


@dataclass
class MatchingResult:
    """Result of a matching operation"""
    matches: List[Match]
    unmatched_entities: List[str]
    total_score: float
    execution_time: float
    
    def get_match_for_entity(self, entity_id: str) -> Optional[Match]:
        """Get match for a specific entity"""
        for match in self.matches:
            if match.entity_a_id == entity_id or match.entity_b_id == entity_id:
                return match
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get matching statistics"""
        return {
            'total_matches': len(self.matches),
            'unmatched_count': len(self.unmatched_entities),
            'average_score': sum(m.score for m in self.matches) / len(self.matches) if self.matches else 0,
            'total_score': self.total_score,
            'execution_time_seconds': self.execution_time
        }
