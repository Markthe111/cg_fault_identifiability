from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_expected_manifest():
    e = json.loads((ROOT / "outputs_expected/major_revision/expected_results.json").read_text())
    assert (e["primary_n_mzi"], e["primary_n_mzii"]) == (48, 72)
    assert (e["dsi_mzi_lt1_count"], e["dsi_mzi_gt2_count"]) == (4, 44)
    assert e["f2_admissible_models"] == ["single_plane", "continuous_segmented"]
    assert len(e["f2_depthwise_spread_exact"]) == 4
