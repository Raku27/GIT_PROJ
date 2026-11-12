"""Stable one-to-one matching over mutually acceptable preference lists."""

from collections import deque
from time import perf_counter

from ..models.entities import Criteria, Entity, Match, MatchingResult
from .scoring import result, score_pair, validate_entities


class GaleShapleyMatcher:
    name = "Gale-Shapley Algorithm"

    def match(
        self, entities_a: list[Entity], entities_b: list[Entity], criteria: Criteria
    ) -> MatchingResult:
        start = perf_counter()
        validate_entities(entities_a, entities_b)
        pairs = {
            (a.id, b.id): score_pair(a, b, criteria)
            for a in entities_a
            for b in entities_b
        }
        eligible = {
            key
            for key, (score, _) in pairs.items()
            if score > 0 and score >= criteria.min_score
        }
        prefs_a = {
            a.id: a.preferences
            if a.preferences is not None
            else sorted(
                [b.id for b in entities_b], key=lambda bid: -pairs[a.id, bid][0]
            )
            for a in entities_a
        }
        prefs_b = {
            b.id: b.preferences
            if b.preferences is not None
            else sorted(
                [a.id for a in entities_a], key=lambda aid: -pairs[aid, b.id][0]
            )
            for b in entities_b
        }
        # Incomplete explicit lists make omitted partners unacceptable. Equal scores use input order.
        ranks = {
            bid: {aid: i for i, aid in enumerate(prefs)}
            for bid, prefs in prefs_b.items()
        }
        prefs_a = {
            aid: [bid for bid in prefs if (aid, bid) in eligible and aid in ranks[bid]]
            for aid, prefs in prefs_a.items()
        }
        free = deque(prefs_a)
        indices = dict.fromkeys(prefs_a, 0)
        engagements = {}
        while free:
            aid = free.popleft()
            while indices[aid] < len(prefs_a[aid]):
                bid = prefs_a[aid][indices[aid]]
                indices[aid] += 1
                current = engagements.get(bid)
                if current is None or ranks[bid][aid] < ranks[bid][current]:
                    engagements[bid] = aid
                    if current is not None:
                        free.append(current)
                    break
        matches = [
            Match(
                aid,
                bid,
                pairs[aid, bid][0],
                {
                    "algorithm": self.name,
                    "stable": True,
                    "attribute_scores": pairs[aid, bid][1],
                },
            )
            for bid, aid in engagements.items()
        ]
        return result(matches, entities_a, entities_b, perf_counter() - start)
