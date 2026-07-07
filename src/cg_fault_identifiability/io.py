"""Input/output helpers."""
import json
import pandas as pd

def load_points_csv(path):
    """Load a point CSV."""
    return pd.read_csv(path)

def load_faults_csv(path):
    """Load a fault CSV."""
    return pd.read_csv(path)

def validate_input_schema(df, required_columns):
    """Validate required columns and raise a clear error if missing."""
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return True

def write_results_with_metadata(results, path, metadata):
    """Write CSV results with adjacent JSON metadata."""
    results.to_csv(path, index=False)
    with open(str(path) + ".metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
