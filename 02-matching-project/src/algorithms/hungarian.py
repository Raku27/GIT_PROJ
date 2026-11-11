"""Maximum-total-score one-to-one assignment using SciPy's assignment solver."""

from time import perf_counter

import numpy as np
from scipy.optimize import linear_sum_assignment

from ..models.entities import Criteria, Entity, Match, MatchingResult
from .scoring import result, score_pair, validate_entities


class HungarianMatcher:
    name = "Hungarian assignment (SciPy solver)"

    def match(
        self, entities_a: list[Entity], entities_b: list[Entity], criteria: Criteria
    ) -> MatchingResult:
        start = perf_counter()
        validate_entities(entities_a, entities_b)
        if not entities_a or not entities_b:
            return result([], entities_a, entities_b, perf_counter() - start)
        pairs = [[score_pair(a, b, criteria) for b in entities_b] for a in entities_a]
        # Zero-value ineligible edges can fill the rectangular assignment, then are omitted.
        # Every partial eligible matching can be completed with such zero-value edges.
        weights = np.array(
            [
                [s if s > 0 and s >= criteria.min_score else 0.0 for s, _ in row]
                for row in pairs
            ]
        )
        rows, cols = linear_sum_assignment(weights, maximize=True)
        matches = [
            Match(
                entities_a[i].id,
                entities_b[j].id,
                float(weights[i, j]),
                {"algorithm": self.name, "attribute_scores": pairs[i][j][1]},
            )
            for i, j in zip(rows, cols)
            if weights[i, j] > 0
        ]
        return result(matches, entities_a, entities_b, perf_counter() - start)
