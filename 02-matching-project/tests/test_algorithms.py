import itertools
import random

import pytest

from example_usage import create_example_entities
from src.algorithms.gale_shapley import GaleShapleyMatcher
from src.algorithms.hungarian import HungarianMatcher
from src.algorithms.scoring import score_pair
from src.models.entities import Criteria, Entity, EntityType

MATCHERS = [HungarianMatcher, GaleShapleyMatcher]


def entity(id, value=None, preferences=None):
    return Entity(
        id, EntityType.USER, {} if value is None else {"x": value}, preferences
    )


@pytest.mark.parametrize("matcher", MATCHERS)
@pytest.mark.parametrize("sizes", [(0, 0), (0, 2), (2, 0), (1, 2), (2, 1), (3, 3)])
def test_empty_and_rectangular(matcher, sizes):
    n, m = sizes
    a = [entity(f"a{i}", 1) for i in range(n)]
    b = [entity(f"b{i}", 1) for i in range(m)]
    r = matcher().match(a, b, Criteria({"x": 1}))
    assert len(r.matches) == min(n, m)
    assert len(r.unmatched_entities) == abs(n - m)
    assert r.total_score == min(n, m)


@pytest.mark.parametrize("matcher", MATCHERS)
def test_missing_fields_are_not_matches(matcher):
    for criteria in [Criteria({"x": 1}), Criteria({"x": 1}, required_attributes=["y"])]:
        r = matcher().match([entity("a")], [entity("b")], criteria)
        assert r.matches == []
        assert r.unmatched_entities == ["a", "b"]


@pytest.mark.parametrize("matcher", MATCHERS)
def test_real_example(matcher):
    a, b = create_example_entities()
    c = Criteria(
        {"skills": 0.4, "experience_years": 0.3, "education": 0.2, "location": 0.1},
        ["skills", "experience_years"],
        min_score=0.5,
        attribute_mappings={
            "skills": "required_skills",
            "experience_years": "min_experience",
            "education": "education_level",
        },
    )
    r = matcher().match(a, b, c)
    assert {(m.entity_a_id, m.entity_b_id) for m in r.matches} == {
        ("candidate_1", "job_1"),
        ("candidate_2", "job_2"),
        ("candidate_3", "job_3"),
    }
    assert r.total_score == pytest.approx(2.8)
    assert all("attribute_scores" in m.details for m in r.matches)


@pytest.mark.parametrize("matcher", MATCHERS)
def test_duplicate_ids_constraints_and_unknown_preferences(matcher):
    with pytest.raises(ValueError, match="unique"):
        matcher().match([entity("same", 1)], [entity("same", 1)], Criteria({"x": 1}))
    a, b = entity("a", 1), entity("b", 1)
    a.constraints = {"capacity": 2}
    with pytest.raises(ValueError, match="constraints"):
        matcher().match([a], [b], Criteria({"x": 1}))
    a.constraints = None
    a.preferences = ["unknown"]
    with pytest.raises(ValueError, match="Preferences"):
        matcher().match([a], [b], Criteria({"x": 1}))


@pytest.mark.parametrize(
    "weights", [{}, {"x": 0}, {"x": -1}, {"x": float("nan")}, {"x": float("inf")}]
)
def test_bad_weights(weights):
    with pytest.raises(ValueError):
        Criteria(weights)


def test_invalid_threshold_capacity_and_normalization():
    for threshold in [-1, 2, float("nan")]:
        with pytest.raises(ValueError):
            Criteria({"x": 1}, min_score=threshold)
    with pytest.raises(ValueError):
        Criteria({"x": 1}, max_matches=2)
    assert Criteria({"x": 2, "y": 2}).weights == {"x": 0.5, "y": 0.5}


def test_assignment_matches_brute_force_partial_optimum():
    rng = random.Random(27)
    for n, m in [(2, 3), (3, 2), (4, 4)]:
        for _ in range(15):
            a = [entity(f"a{i}", rng.randrange(20)) for i in range(n)]
            b = [entity(f"b{i}", rng.randrange(20)) for i in range(m)]
            c = Criteria({"x": 1}, min_score=0.5)
            scores = [[score_pair(x, y, c)[0] for y in b] for x in a]
            # Exhaustively enumerate every partial injective assignment, including unmatched choices.
            best = 0
            for choices in itertools.product(range(-1, m), repeat=n):
                used = [i for i in choices if i >= 0]
                if len(used) != len(set(used)):
                    continue
                if any(
                    scores[i][j] < c.min_score for i, j in enumerate(choices) if j >= 0
                ):
                    continue
                best = max(
                    best, sum(scores[i][j] for i, j in enumerate(choices) if j >= 0)
                )
            r = HungarianMatcher().match(a, b, c)
            assert r.total_score == pytest.approx(best)


def test_explicit_and_incomplete_preferences():
    a = entity("a", 1, ["b2"])
    b1, b2 = entity("b1", 1, ["a"]), entity("b2", 1, ["a"])
    r = GaleShapleyMatcher().match([a], [b1, b2], Criteria({"x": 1}))
    assert r.matches[0].entity_b_id == "b2"
    b2.preferences = []
    assert GaleShapleyMatcher().match([a], [b1, b2], Criteria({"x": 1})).matches == []


def test_stability_no_blocking_pair_with_incomplete_preferences_and_threshold():
    rng = random.Random(42)
    for _ in range(40):
        a = [entity(f"a{i}", rng.randrange(10)) for i in range(5)]
        b = [entity(f"b{i}", rng.randrange(10)) for i in range(4)]
        for group, other in [(a, b), (b, a)]:
            for e in group:
                e.preferences = rng.sample(
                    [x.id for x in other], rng.randrange(len(other) + 1)
                )
        c = Criteria({"x": 1}, min_score=0.5)
        r = GaleShapleyMatcher().match(a, b, c)
        partners = {
            i: j
            for match in r.matches
            for i, j in [
                (match.entity_a_id, match.entity_b_id),
                (match.entity_b_id, match.entity_a_id),
            ]
        }
        for x in a:
            for y in b:
                score, _ = score_pair(x, y, c)
                if (
                    score <= 0
                    or score < c.min_score
                    or y.id not in x.preferences
                    or x.id not in y.preferences
                ):
                    continue
                x_prefers = x.id not in partners or x.preferences.index(
                    y.id
                ) < x.preferences.index(partners[x.id])
                y_prefers = y.id not in partners or y.preferences.index(
                    x.id
                ) < y.preferences.index(partners[y.id])
                assert not (x_prefers and y_prefers)


def test_shared_scores_and_nonfinite_numeric_attributes():
    a, b = entity("a", 10), entity("b", 8)
    c = Criteria({"x": 1})
    assert (
        HungarianMatcher().match([a], [b], c).total_score
        == GaleShapleyMatcher().match([a], [b], c).total_score
    )
    a.attributes["x"] = float("inf")
    with pytest.raises(ValueError, match="finite"):
        score_pair(a, b, c)


def test_portfolio_tradeoff_has_distinct_objectives():
    from examples.algorithm_tradeoff import compare_objectives

    outcomes = compare_objectives()
    assert outcomes["hungarian"]["pairs"] == [["a1", "b1"], ["a2", "b2"]]
    assert outcomes["hungarian"]["total_score"] == 2.0
    assert {tuple(p) for p in outcomes["gale_shapley"]["pairs"]} == {
        ("a1", "b2"),
        ("a2", "b1"),
    }
    assert outcomes["gale_shapley"]["total_score"] == pytest.approx(0.2)
