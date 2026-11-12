"""Shared scoring and eligibility; mappings go from group A to group B."""

import math
from numbers import Real

from ..models.entities import Criteria, Entity, MatchingResult


def validate_entities(a: list[Entity], b: list[Entity]) -> None:
    ids = [e.id for e in a + b]
    if any(not i.strip() for i in ids) or len(ids) != len(set(ids)):
        raise ValueError("Entity IDs must be nonblank and unique across both groups")
    for group, other in ((a, b), (b, a)):
        allowed = {e.id for e in other}
        for e in group:
            if e.constraints:
                raise ValueError(
                    "Custom constraints are not supported; use required_attributes and min_score"
                )
            if e.preferences is not None and (
                len(e.preferences) != len(set(e.preferences))
                or not set(e.preferences) <= allowed
            ):
                raise ValueError(
                    "Preferences must contain unique IDs from the opposite group"
                )


def compare(a, b, target: str) -> float:
    if a is None or b is None:
        return 0.0
    if isinstance(a, bool) or isinstance(b, bool):
        return float(type(a) is type(b) and a == b)
    if isinstance(a, Real) and isinstance(b, Real):
        if not math.isfinite(a) or not math.isfinite(b):
            raise ValueError("Numeric attributes must be finite")
        if target == "min_experience":
            return float(a >= b)
        return max(0.0, 1.0 - abs(a - b) / max(abs(a), abs(b), 1.0))
    if isinstance(a, str) and isinstance(b, str):
        return float(bool(a.strip()) and a.strip().casefold() == b.strip().casefold())
    if isinstance(a, list) and isinstance(b, list):
        x = {str(v).strip().casefold() for v in a if str(v).strip()}
        y = {str(v).strip().casefold() for v in b if str(v).strip()}
        denominator = len(y) if target == "required_skills" else len(x | y)
        return len(x & y) / denominator if denominator else 0.0
    return float(type(a) is type(b) and a == b)


def score_pair(
    a: Entity, b: Entity, criteria: Criteria
) -> tuple[float, dict[str, float]]:
    for key in criteria.required_attributes:
        if (
            a.get_attribute(key) is None
            or b.get_attribute(criteria.attribute_mappings.get(key, key)) is None
        ):
            return 0.0, {}
    scores = {
        key: compare(
            a.get_attribute(key),
            b.get_attribute(criteria.attribute_mappings.get(key, key)),
            criteria.attribute_mappings.get(key, key),
        )
        for key in criteria.weights
    }
    return criteria.calculate_weighted_score(scores), scores


def result(matches, a, b, elapsed):
    matched = {i for m in matches for i in (m.entity_a_id, m.entity_b_id)}
    return MatchingResult(
        matches,
        [e.id for e in a + b if e.id not in matched],
        sum(m.score for m in matches),
        elapsed,
    )
