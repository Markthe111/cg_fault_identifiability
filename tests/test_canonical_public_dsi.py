from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_primary_canonical_dsi():
    d = pd.read_csv(ROOT / "data/real_case_public_derived/REAL_CASE_DSI_PRIMARY_PUBLIC.csv")
    assert d.groupby("zone").size().to_dict() == {"MZ-I": 48, "MZ-II": 72}
    assert np.isclose(d.query("zone == 'MZ-I'").dsi.median(), 6.730056, rtol=0, atol=1e-6)
    assert np.isclose(d.query("zone == 'MZ-II'").dsi.median(), 15.290964, rtol=0, atol=1e-6)
    assert int(d.query("zone == 'MZ-I'").dsi_lt_1.sum()) == 4
    assert int(d.query("zone == 'MZ-I'").dsi_gt_2.sum()) == 44
    assert np.allclose(d.dsi, d.d_plan_competing_m / d.d_plan_associated_m, rtol=0, atol=1e-9)
    assert (d.dsi < 1).any()
    assert "second" not in " ".join(d.columns).lower()
