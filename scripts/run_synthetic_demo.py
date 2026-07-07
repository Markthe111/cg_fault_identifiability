from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cg_fault_identifiability.synthetic import generate_boundary_sensitive_case, export_synthetic_case

if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "outputs_expected" / "synthetic_demo"
    case = generate_boundary_sensitive_case({"fault_separation": 800, "n_per_zone": 80}, seed=20260705)
    export_synthetic_case(case, out)
    print(f"Wrote synthetic demo to {out}")
