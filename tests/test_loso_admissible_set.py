from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_admissible_set_and_sections():
    a = pd.read_csv(ROOT / "outputs_expected/major_revision/loso_admissible_set_expected.csv")
    f2 = set(a[(a.fault == "F2") & a.admissible].model_family)
    assert f2 == {"single_plane", "segmented_plane"}
    m = pd.read_csv(ROOT / "outputs_expected/major_revision/loso_model_family_summary_expected.csv")
    assert m.groupby("fault").n_sections.first().astype(int).to_dict() == {"F2": 8, "F7": 3}
    assert a[a.fault.eq("F7")].F7_inference_limit.str.contains("limited discrimination").all()
