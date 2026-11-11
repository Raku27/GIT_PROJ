"""Show why maximizing similarity and honoring stable preferences are different objectives."""

import json

from src.algorithms.gale_shapley import GaleShapleyMatcher
from src.algorithms.hungarian import HungarianMatcher
from src.models.entities import Criteria, Entity, EntityType


def compare_objectives():
    a = [
        Entity("a1", EntityType.USER, {"x": 10}, ["b2", "b1"]),
        Entity("a2", EntityType.USER, {"x": 1}, ["b1", "b2"]),
    ]
    b = [
        Entity("b1", EntityType.ITEM, {"x": 10}, ["a2", "a1"]),
        Entity("b2", EntityType.ITEM, {"x": 1}, ["a1", "a2"]),
    ]
    criteria = Criteria({"x": 1})
    return {
        name: {
            "pairs": [[m.entity_a_id, m.entity_b_id] for m in result.matches],
            "total_score": result.total_score,
        }
        for name, result in [
            ("hungarian", HungarianMatcher().match(a, b, criteria)),
            ("gale_shapley", GaleShapleyMatcher().match(a, b, criteria)),
        ]
    }


if __name__ == "__main__":
    print(json.dumps(compare_objectives(), indent=2))
