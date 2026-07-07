import subprocess, sys
from pathlib import Path
here = Path(__file__).resolve().parent
subprocess.check_call([sys.executable, str(here / "run_synthetic_demo.py")])
subprocess.check_call([sys.executable, str(here / "run_dsi_benchmark.py"), "--quick"])
