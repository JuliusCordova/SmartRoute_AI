"""Pure deterministic route evaluator — no GCP, network, Maps or Firestore."""
import pytest
from pydantic import ValidationError
from app.optimization import EvaluationInput, evaluate_synthetic_route


def test_ortools_improves_obviously_suboptimal_baseline():
    # depot 0, synthetic stops A/B/C; asymmetric matrix allowed.
    matrix = [
        [0, 1, 10, 10],
        [1, 0, 1, 10],
        [10, 10, 0, 1],
        [1, 10, 10, 0],
    ]
    data = EvaluationInput(order_ids=["A", "C", "B"], durations_seconds=matrix)
    result = evaluate_synthetic_route(data)
    assert result.data_origin == "synthetic"
    assert set(result.ordered_order_ids) == {"A", "B", "C"}
    assert len(result.ordered_order_ids) == 3
    assert result.optimized_seconds <= result.baseline_seconds
    assert len(result.matrix_fingerprint) == 64
    assert "optimum" in result.warnings[0]


def test_fingerprint_is_repeatable():
    p = EvaluationInput(order_ids=["A"], durations_seconds=[[0, 30], [20, 0]])
    a, b = evaluate_synthetic_route(p), evaluate_synthetic_route(p)
    assert a.model_dump() == b.model_dump()
    assert a.baseline_seconds == 50
    assert a.optimized_seconds == 50
    assert a.improvement_pct == 0.0


@pytest.mark.parametrize("kwargs", [
    {"order_ids": ["A", "B"], "durations_seconds": [[0, 10], [10, 0]]},
    {"order_ids": ["A", "A"], "durations_seconds": [[0, 1, 1], [1, 0, 1], [1, 1, 0]]},
    {"order_ids": ["A"], "durations_seconds": [[1, 1], [1, 0]]},
    {"order_ids": ["A"], "durations_seconds": [[0, -1], [1, 0]]},
    {"order_ids": ["A"], "durations_seconds": [[0, 1], [1, 0]], "data_origin": "observed"},
])
def test_invalid_fixtures_rejected(kwargs):
    with pytest.raises(ValidationError):
        EvaluationInput(**kwargs)
