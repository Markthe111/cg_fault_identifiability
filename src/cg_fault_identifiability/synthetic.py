"""Synthetic data generation."""
import json
import numpy as np
import pandas as pd

def generate_two_fault_domain_case(config, seed):
    """Generate two opposite-domain ore point clouds and fault constraints in arbitrary local coordinates."""
    rng = np.random.default_rng(seed)
    n = config.get("n_per_zone", 80)
    sep = config.get("fault_separation", 800.0)
    rows = []
    for zone, fault, center in [("Zone_A", "F_left", 80.0), ("Zone_B", "F_right", sep - 80.0)]:
        for i in range(n):
            rows.append({"point_id": f"{zone}_{i:03d}", "zone": zone, "expected_fault": fault, "x": rng.normal(center, 35), "y": rng.uniform(0, 1000), "z": rng.uniform(-400, -50)})
    ore = pd.DataFrame(rows)
    fpts = []
    for fault, x0 in [("F_left", 0.0), ("F_right", sep)]:
        for sec in range(6):
            y = sec * 180.0
            for k in range(12):
                fpts.append({"fault": fault, "section": f"S{sec}", "x": x0 + rng.normal(0, 8), "y": y + rng.normal(0, 4), "z": -30 - 30 * k + rng.normal(0, 8)})
    return {"ore_points": ore, "fault_points": pd.DataFrame(fpts), "faults": {"F_left": {"x": 0.0}, "F_right": {"x": sep}}, "config": config}

def generate_boundary_sensitive_case(config, seed):
    """Generate a case with a small cluster near the attribution boundary."""
    case = generate_two_fault_domain_case(config, seed)
    rng = np.random.default_rng(seed + 1)
    sep = config.get("fault_separation", 800.0)
    extra = pd.DataFrame({"point_id": [f"Boundary_{i:03d}" for i in range(20)], "zone": "Zone_A", "expected_fault": "F_left", "x": rng.normal(sep / 2.2, 15, 20), "y": rng.uniform(0, 1000, 20), "z": rng.uniform(-300, -50, 20)})
    case["ore_points"] = pd.concat([case["ore_points"], extra], ignore_index=True)
    return case

def generate_multifault_case(config, seed):
    """Generate a two-domain case with additional non-associated faults."""
    case = generate_boundary_sensitive_case(config, seed)
    sep = config.get("fault_separation", 800.0)
    case["faults"].update({"F_mid": {"x": sep / 2}, "F_far": {"x": sep * 1.4}})
    return case

def export_synthetic_case(case, out_dir):
    """Write synthetic case tables to disk."""
    import pathlib
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    case["ore_points"].to_csv(out / "synthetic_ore_points.csv", index=False)
    case["fault_points"].to_csv(out / "synthetic_fault_points.csv", index=False)
    pd.DataFrame([{"fault": k, **v} for k, v in case["faults"].items()]).to_csv(out / "synthetic_faults.csv", index=False)
    pd.DataFrame({"section": sorted(case["fault_points"]["section"].unique())}).to_csv(out / "synthetic_sections.csv", index=False)
    (out / "synthetic_config.json").write_text(json.dumps(case["config"], indent=2), encoding="utf-8")
