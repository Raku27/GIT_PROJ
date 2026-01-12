"""
Hungarian Algorithm for Optimal Assignment
Solves the assignment problem for bipartite matching
"""

import numpy as np
from scipy.optimize import linear_sum_assignment
from typing import List, Dict, Tuple
import time

from ..models.entities import Entity, Match, MatchingResult, Criteria


class HungarianMatcher:
    """Hungarian algorithm implementation for optimal matching"""
    
    def __init__(self):
        """Initialize the Hungarian matcher"""
        self.name = "Hungarian Algorithm"
    
    def _calculate_cost_matrix(self, entities_a: List[Entity], entities_b: List[Entity], 
                               criteria: Criteria) -> np.ndarray:
        """
        Calculate cost matrix between two sets of entities
        
        Args:
            entities_a: First set of entities
            entities_b: Second set of entities
            criteria: Matching criteria
            
        Returns:
            Cost matrix where cost[i][j] is the cost of matching entities_a[i] with entities_b[j]
        """
        n = len(entities_a)
        m = len(entities_b)
        
        # Create cost matrix (we'll use negative of score as cost for minimization)
        cost_matrix = np.zeros((n, m))
        
        for i, entity_a in enumerate(entities_a):
            for j, entity_b in enumerate(entities_b):
                # Calculate similarity score
                score = self._calculate_similarity(entity_a, entity_b, criteria)
                # Use negative score as cost (we want to minimize cost = maximize score)
                cost_matrix[i][j] = -score
        
        return cost_matrix
    
    def _calculate_similarity(self, entity_a: Entity, entity_b: Entity, 
                              criteria: Criteria) -> float:
        """
        Calculate similarity score between two entities
        
        Args:
            entity_a: First entity
            entity_b: Second entity
            criteria: Matching criteria
            
        Returns:
            Similarity score between 0 and 1
        """
        scores = {}
        
        # Calculate scores for each attribute
        for attribute in criteria.weights.keys():
            score = self._compare_attribute(
                entity_a.get_attribute(attribute),
                entity_b.get_attribute(attribute),
                attribute
            )
            scores[attribute] = score
        
        # Check required attributes
        for req_attr in criteria.required_attributes:
            if req_attr not in entity_a.attributes or req_attr not in entity_b.attributes:
                return 0.0  # Missing required attribute
        
        # Calculate weighted score
        weighted_score = criteria.calculate_weighted_score(scores)
        
        # Apply minimum score threshold
        if weighted_score < criteria.min_score:
            return 0.0
        
        return weighted_score
    
    def _compare_attribute(self, value_a: Any, value_b: Any, attribute: str) -> float:
        """
        Compare two attribute values and return similarity score
        
        Args:
            value_a: Value from first entity
            value_b: Value from second entity
            attribute: Attribute name
            
        Returns:
            Similarity score between 0 and 1
        """
        # Handle None values
        if value_a is None or value_b is None:
            return 0.0
        
        # Numeric comparison
        if isinstance(value_a, (int, float)) and isinstance(value_b, (int, float)):
            # Normalize difference (assuming max difference of 100)
            diff = abs(value_a - value_b)
            max_diff = 100.0  # Adjust based on your data range
            return max(0.0, 1.0 - (diff / max_diff))
        
        # String comparison
        if isinstance(value_a, str) and isinstance(value_b, str):
            if value_a.lower() == value_b.lower():
                return 1.0
            # Partial match
            if value_a.lower() in value_b.lower() or value_b.lower() in value_a.lower():
                return 0.5
            return 0.0
        
        # List comparison (for skills, interests, etc.)
        if isinstance(value_a, list) and isinstance(value_b, list):
            set_a = set(str(v).lower() for v in value_a)
            set_b = set(str(v).lower() for v in value_b)
            if not set_a or not set_b:
                return 0.0
            intersection = len(set_a & set_b)
            union = len(set_a | set_b)
            return intersection / union if union > 0 else 0.0
        
        # Default: exact match
        return 1.0 if value_a == value_b else 0.0
    
    def match(self, entities_a: List[Entity], entities_b: List[Entity], 
              criteria: Criteria) -> MatchingResult:
        """
        Perform optimal matching using Hungarian algorithm
        
        Args:
            entities_a: First set of entities to match
            entities_b: Second set of entities to match
            criteria: Matching criteria
            
        Returns:
            MatchingResult with optimal matches
        """
        start_time = time.time()
        
        if not entities_a or not entities_b:
            return MatchingResult(
                matches=[],
                unmatched_entities=[e.id for e in entities_a + entities_b],
                total_score=0.0,
                execution_time=time.time() - start_time
            )
        
        # Calculate cost matrix
        cost_matrix = self._calculate_cost_matrix(entities_a, entities_b, criteria)
        
        # Handle rectangular matrices (different sizes)
        n, m = cost_matrix.shape
        
        if n > m:
            # More entities in A than B - pad B side
            padding = np.full((n, n - m), np.inf)
            cost_matrix = np.hstack([cost_matrix, padding])
        elif m > n:
            # More entities in B than A - pad A side
            padding = np.full((m - n, m), np.inf)
            cost_matrix = np.vstack([cost_matrix, padding])
        
        # Solve assignment problem
        row_indices, col_indices = linear_sum_assignment(cost_matrix)
        
        # Extract matches
        matches = []
        matched_a = set()
        matched_b = set()
        total_score = 0.0
        
        for i, j in zip(row_indices, col_indices):
            if i < len(entities_a) and j < len(entities_b):
                # Calculate actual score (negate cost)
                score = -cost_matrix[i][j]
                
                if score > 0 and score >= criteria.min_score:
                    match = Match(
                        entity_a_id=entities_a[i].id,
                        entity_b_id=entities_b[j].id,
                        score=score,
                        details={
                            'algorithm': self.name,
                            'entity_a_type': entities_a[i].entity_type.value,
                            'entity_b_type': entities_b[j].entity_type.value
                        }
                    )
                    matches.append(match)
                    matched_a.add(i)
                    matched_b.add(j)
                    total_score += score
        
        # Find unmatched entities
        unmatched = []
        for i, entity in enumerate(entities_a):
            if i not in matched_a:
                unmatched.append(entity.id)
        for j, entity in enumerate(entities_b):
            if j not in matched_b:
                unmatched.append(entity.id)
        
        execution_time = time.time() - start_time
        
        return MatchingResult(
            matches=matches,
            unmatched_entities=unmatched,
            total_score=total_score,
            execution_time=execution_time
        )
