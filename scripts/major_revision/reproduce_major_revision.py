from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproduce the frozen C&G major-revision analyses.")
    parser.add_argument("--seed", type=int, default=20260806)
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT / "outputs" / "major_revision")
    args = parser.parse_args()
    out = args.output_root.resolve()
    scripts = Path(__file__).resolve().parent
    commands = [
        [sys.executable, str(scripts / "run_diagnostic_validation.py"), "--seed", str(args.seed), "--output-root", str(out)],
        [sys.executable, str(scripts / "run_ood_validation.py"), "--seed", str(args.seed), "--output-root", str(out)],
        [sys.executable, str(scripts / "run_loso_geometry_comparison.py"), "--seed", str(args.seed), "--output-root", str(out)],
    ]
    for command in commands:
        subprocess.run(command, cwd=REPO_ROOT, check=True)
    copies = {
        out / "phase2" / "heldout_pooled_metrics.csv": out / "diagnostic_metrics.csv",
        out / "phase2" / "calibration_bins.csv": out / "diagnostic_calibration.csv",
        out / "phase3" / "OOD_diagnostic_performance.csv": out / "ood_metrics.csv",
        out / "phase3" / "OOD_calibration_bins.csv": out / "ood_calibration.csv",
        out / "phase5" / "model_family_summary.csv": out / "loso_model_family_summary.csv",
        out / "phase5" / "admissible_model_set.csv": out / "loso_admissible_set.csv",
        out / "phase5" / "depthwise_geometry_spread_summary.csv": out / "depthwise_geometry_spread.csv",
    }
    for source, target in copies.items():
        target.write_bytes(source.read_bytes())
    summary = {
        "status": "PASS", "seed": args.seed,
        "ood_refit": False, "ood_recalibration": False, "ood_retuning": False,
        "generated_outputs": [str(path.relative_to(out)) for path in copies.values()],
    }
    (out / "major_revision_reproduction_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("MAJOR_REVISION_REPRODUCTION_PASS")


if __name__ == "__main__":
    main()
