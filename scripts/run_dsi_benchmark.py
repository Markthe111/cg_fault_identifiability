from pathlib import Path
import argparse, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cg_fault_identifiability.benchmark import run_dsi_stability_grid, summarize_operating_regions

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    cfg = {"seed_base": 20260705, "n_replicates": 4 if args.quick else 20, "n_mc": 50 if args.quick else 200}
    out = Path(__file__).resolve().parents[1] / "outputs_expected" / "dsi_benchmark"
    out.mkdir(parents=True, exist_ok=True)
    df = run_dsi_stability_grid(cfg)
    df.to_csv(out / "DSI_BENCHMARK_RAW_RESULTS.csv", index=False)
    summarize_operating_regions(df).to_csv(out / "DSI_OPERATING_REGIONS.csv", index=False)
    print(f"Wrote benchmark outputs to {out}")
