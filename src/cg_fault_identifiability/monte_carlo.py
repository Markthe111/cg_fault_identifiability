"""Monte Carlo perturbation workflows for fault-domain assignment stability.

The paper uses fixed-seed perturbations to evaluate whether assignment to an
associated fault remains stable under plausible geometry perturbations.
"""

from __future__ import annotations

from .perturbation import run_monte_carlo_attribution, sample_fault_parameters

__all__ = ["sample_fault_parameters", "run_monte_carlo_attribution"]
