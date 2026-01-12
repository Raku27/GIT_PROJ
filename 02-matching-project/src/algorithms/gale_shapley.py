"""
Gale-Shapley Algorithm for Stable Matching
Implements the stable marriage problem algorithm
"""

from typing import List, Dict, Set
import time

from ..models.entities import Entity, Match, MatchingResult, Criteria, EntityType


class GaleShapleyMatcher:
    """Gale-Shapley algorithm for stable matching"""
    
    def __init__(self):
        """Initialize the Gale-Shapley matcher"""
        self.name = "Gale-Shapley Algorithm"
    
    def _build_preference_lists(self, entities_a: List[Entity], entities_b: List[Entity],
                                criteria: Criteria) -> Dict[str, List[str]]:
        """
        Build preference lists for each entity
        
        Args:
            entities_a: First set of entities (proposers)
            entities_b: Second set of entities (acceptors)
            criteria: Matching criteria
            
        Returns:
            Dictionary mapping entity IDs to their preference lists
        """
        preferences = {}
        
        for entity_a in entities_a:
            # Calculate scores for all entities in B
            scores = []
            for entity_b in entities_b:
                score = self._calculate_similarity(entity_a, entity_b, criteria)
                scores.append((entity_b.id, score))
            
            # Sort by score (descending) to create preference list
            scores.sort(key=lambda x: x[1], reverse=True)
            preferences[entity_a.id] = [entity_id for entity_id, _ in scores]
        
        for entity_b in entities_b:
            # Calculate scores for all entities in A
            scores = []
            for entity_a in entities_a:
                score = self._calculate_similarity(entity_b, entity_a, criteria)
                scores.append((entity_a.id, score))
            
            # Sort by score (descending)
            scores.sort(key=lambda x: x[1], reverse=True)
            preferences[entity_b.id] = [entity_id for entity_id, _ in scores]
        
        return preferences
    
    def _calculate_similarity(self, entity_a: Entity, entity_b: Entity,
                              criteria: Criteria) -> float:
        """Calculate similarity score between two entities"""
        scores = {}
        
        for attribute in criteria.weights.keys():
            value_a = entity_a.get_attribute(attribute)
            value_b = entity_b.get_attribute(attribute)
            
            # Simple comparison
            if value_a == value_b:
                score = 1.0
            elif isinstance(value_a, (int, float)) and isinstance(value_b, (int, float)):
                diff = abs(value_a - value_b)
                max_diff = 100.0
                score = max(0.0, 1.0 - (diff / max_diff))
            else:
                score = 0.5 if value_a and value_b else 0.0
            
            scores[attribute] = score
        
        # Check required attributes
        for req_attr in criteria.required_attributes:
            if req_attr not in entity_a.attributes or req_attr not in entity_b.attributes:
                return 0.0
        
        return criteria.calculate_weighted_score(scores)
    
    def match(self, entities_a: List[Entity], entities_b: List[Entity],
              criteria: Criteria) -> MatchingResult:
        """
        Perform stable matching using Gale-Shapley algorithm
        
        Args:
            entities_a: First set of entities (proposers)
            entities_b: Second set of entities (acceptors)
            criteria: Matching criteria
            
        Returns:
            MatchingResult with stable matches
        """
        start_time = time.time()
        
        if not entities_a or not entities_b:
            return MatchingResult(
                matches=[],
                unmatched_entities=[e.id for e in entities_a + entities_b],
                total_score=0.0,
                execution_time=time.time() - start_time
            )
        
        # Build preference lists
        preferences = self._build_preference_lists(entities_a, entities_b, criteria)
        
        # Create entity lookup
        entity_map = {e.id: e for e in entities_a + entities_b}
        
        # Initialize: all proposers are free
        free_proposers = [e.id for e in entities_a]
        engagements = {}  # acceptor_id -> proposer_id
        proposer_index = {pid: 0 for pid in free_proposers}  # Track proposal index
        
        # Main algorithm loop
        while free_proposers:
            proposer_id = free_proposers[0]
            proposer_prefs = preferences[proposer_id]
            
            # Proposer has exhausted all options
            if proposer_index[proposer_id] >= len(proposer_prefs):
                free_proposers.pop(0)
                continue
            
            # Get next preferred acceptor
            acceptor_id = proposer_prefs[proposer_index[proposer_id]]
            proposer_index[proposer_id] += 1
            
            # If acceptor is free, engage
            if acceptor_id not in engagements:
                engagements[acceptor_id] = proposer_id
                free_proposers.pop(0)
            else:
                # Acceptor is engaged, check if new proposer is preferred
                current_proposer = engagements[acceptor_id]
                acceptor_prefs = preferences[acceptor_id]
                
                if acceptor_prefs.index(proposer_id) < acceptor_prefs.index(current_proposer):
                    # New proposer is preferred, swap
                    engagements[acceptor_id] = proposer_id
                    free_proposers.pop(0)
                    free_proposers.append(current_proposer)
                # Otherwise, proposer remains free and tries next
        
        # Build matches
        matches = []
        total_score = 0.0
        
        for acceptor_id, proposer_id in engagements.items():
            entity_a = entity_map[proposer_id]
            entity_b = entity_map[acceptor_id]
            
            score = self._calculate_similarity(entity_a, entity_b, criteria)
            
            if score >= criteria.min_score:
                match = Match(
                    entity_a_id=proposer_id,
                    entity_b_id=acceptor_id,
                    score=score,
                    details={
                        'algorithm': self.name,
                        'stable': True
                    }
                )
                matches.append(match)
                total_score += score
        
        # Find unmatched entities
        matched_ids = {m.entity_a_id for m in matches} | {m.entity_b_id for m in matches}
        unmatched = [e.id for e in entities_a + entities_b if e.id not in matched_ids]
        
        execution_time = time.time() - start_time
        
        return MatchingResult(
            matches=matches,
            unmatched_entities=unmatched,
            total_score=total_score,
            execution_time=execution_time
        )
