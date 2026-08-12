from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]


def test_ood_fit_is_id_only_and_no_ood_retune():
    path = ROOT / "scripts/major_revision/run_ood_validation.py"
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    fits = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "fit"]
    assert len(fits) == 1
    fit_source = ast.get_source_segment(text, fits[0])
    assert "y_id" in fit_source and "y_ood" not in fit_source
    assert "no OOD retuning" in text
    assert "ood[metric]" not in text.split("model.fit", 1)[0].split("for metric in METRICS:", 1)[1]
