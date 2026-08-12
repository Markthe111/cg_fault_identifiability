from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_public_coordinates_are_local_and_origin_absent():
    folder = ROOT / "data/major_revision/loso_coordinate_shifted"
    for path in folder.glob("*.csv"):
        d = pd.read_csv(path)
        assert not {"Easting", "Northing", "longitude", "latitude", "EPSG", "origin_x", "origin_y"}.intersection(d.columns)
        for col in [c for c in d.columns if c in {"X", "Y"}]:
            assert d[col].abs().max() < 10000


def test_depthwise_expected_output_is_coordinate_free():
    path = ROOT / "outputs_expected/major_revision/depthwise_geometry_spread_expected.csv"
    d = pd.read_csv(path)
    assert list(d.columns) == [
        "fault", "depth_below_trace_m", "admissible_model_count",
        "median_x_spread_m", "maximum_x_spread_m",
    ]
    assert len(d) == 8
    assert d.groupby("fault")["depth_below_trace_m"].nunique().to_dict() == {"F2": 4, "F7": 4}
