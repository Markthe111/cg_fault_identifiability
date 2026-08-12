from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_grouped_expected_metrics():
    d = pd.read_csv(ROOT / "outputs_expected/major_revision/diagnostic_metrics_expected.csv")
    q = d[d.scheme.eq("competing_fault_count_family")].set_index("metric")
    for metric, expected in {"distance_diff_3D": (0.981, 0.994, 0.049), "DSI_2D": (0.875, 0.949, 0.114)}.items():
        got = q.loc[metric, ["roc_auc", "pr_auc", "brier_score"]].astype(float).round(3).tolist()
        assert got == list(expected)
