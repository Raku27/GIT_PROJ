from copy import deepcopy

import pytest
from fastapi.testclient import TestClient
from src.api.main import HungarianMatcher, app

client = TestClient(app)


def payload():
    return {
        "entities_a": [
            {
                "id": "a",
                "entity_type": "candidate",
                "attributes": {"skills": ["Python"]},
            }
        ],
        "entities_b": [
            {
                "id": "b",
                "entity_type": "job",
                "attributes": {"required_skills": ["Python"]},
            }
        ],
        "criteria": {
            "weights": {"skills": 1},
            "attribute_mappings": {"skills": "required_skills"},
        },
    }


@pytest.mark.parametrize("algorithm", ["hungarian", "gale_shapley"])
def test_api_success(algorithm):
    data = payload()
    data["algorithm"] = algorithm
    r = client.post("/api/match", json=data)
    assert r.status_code == 200
    assert r.json()["total_score"] == 1
    assert r.json()["matches"][0]["entity_b_id"] == "b"
    assert client.get("/health").json() == {"status": "healthy"}
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/").status_code == 200


@pytest.mark.parametrize(
    "change",
    [
        "algorithm",
        "type",
        "weights",
        "threshold",
        "capacity",
        "duplicate",
        "constraints",
        "count",
        "size",
        "preferences",
        "extra",
    ],
)
def test_bad_requests_are_client_errors(change):
    data = payload()
    if change == "algorithm":
        data["algorithm"] = "unknown"
    if change == "type":
        data["entities_a"][0]["entity_type"] = "invalid"
    if change == "weights":
        data["criteria"]["weights"] = {"skills": -1}
    if change == "threshold":
        data["criteria"]["min_score"] = 2
    if change == "capacity":
        data["criteria"]["max_matches"] = 2
    if change == "duplicate":
        data["entities_b"][0]["id"] = "a"
    if change == "constraints":
        data["entities_a"][0]["constraints"] = {"capacity": 3}
    if change == "count":
        data["entities_a"] = [deepcopy(data["entities_a"][0]) for _ in range(201)]
    if change == "size":
        data["entities_a"][0]["attributes"]["large"] = "x" * 10001
    if change == "preferences":
        data["entities_a"][0]["preferences"] = ["unknown"]
    if change == "extra":
        data["surprise"] = True
    assert client.post("/api/match", json=data).status_code == 422


def test_internal_errors_hide_details(monkeypatch):
    def fail(*args):
        raise RuntimeError("secret-internal-path")

    monkeypatch.setattr(HungarianMatcher, "match", fail)
    response = client.post("/api/match", json=payload())
    assert response.status_code == 500
    assert "secret-internal-path" not in response.text
    assert response.json()["detail"]["request_id"]


@pytest.mark.parametrize("number", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_weights_return_validation_error(number):
    import json

    body = json.dumps(payload()).replace('"skills": 1', '"skills": ' + number)
    response = client.post(
        "/api/match", content=body, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422
