# Source script inventory

This inventory records the project scripts found during repository preparation
and how they map to the public release package.

| Source script | Function | Dependencies | Release status |
|---|---|---|---|
| `paper2_structural_identifiability_v1/scripts/run_structural_identifiability_package.py` | End-to-end project pipeline for standardized data, fault network, ensemble assignment, LOSO, DSI summaries, tables and reports | numpy, pandas, matplotlib, statsmodels | Documented as provenance. Not copied as-is because it depends on restricted project paths and data. |
| `structural_observation_pipeline_v1/scripts/v0_build_F2_F7_domain.py` | Early F2/F7 domain construction | numpy, pandas, matplotlib | Logic represented in `fault_surface.py` and `attribution.py`. |
| `structural_observation_pipeline_v1/scripts/v0_build_true_attitude_faults_dem.py` | True-attitude fault construction | numpy, pandas | Documented as provenance; DEM/source inputs are not public. |
| `structural_observation_pipeline_v1/scripts/v0_ensemble_3way_perturbation.py` | Perturbation ensemble | numpy, pandas | Logic represented in `monte_carlo.py` and `perturbation.py`. |
| `structural_observation_pipeline_v1/scripts/v0_model_ensemble_domain_probability.py` | Ensemble domain-probability summaries | numpy, pandas | Logic represented in `monte_carlo.py` and `attribution.py`. |
| `structural_observation_pipeline_v1/v0_domain_model/v0_ensemble_regularized.py` | Regularized 500-model ensemble outputs | numpy, pandas | Documented as provenance; not copied because it uses restricted local paths. |
| `paper2_figures/make_paper2_figures.py` | Main figure builder | numpy, pandas, matplotlib | Documented as provenance; public repository includes figure data/outputs where releasable. |
| `paper2_figures/fig4_geometric_distance_final_v2.py` | Final single best-fit 3D distance Figure 4 | numpy, pandas, matplotlib | Documented as provenance; not copied because it depends on real ore point files. |
| `paper2_figures/3d_model/domain_attribution_figure_materials/render_domain_attribution_pyvista.py` | 3D domain-attribution rendering | numpy, pandas, pyvista | Documented as provenance. PyVista rendering is optional and not needed for the synthetic code tests. |
| `paper2_figures/3d_model/route_b/route_b_planar_fault_surfaces.py` | Mapped-attitude planar fault surfaces | numpy, pandas, pyvista | Logic represented in Eq. 1 fault-surface module. |
| `paper2_figures/3d_model/route_b_fit/route_b_fit_ols_fault_surfaces.py` | OLS fitted fault planes | numpy, pandas, pyvista | Plane fitting represented in `fault_surface.py`; variance utilities in `variance.py`. |
| `paper2_cg_innovation_upgrade_v1/run_phase_p2_cg_b1.py` | Generator for B1 synthetic benchmark and reproducibility package | numpy, pandas, matplotlib | Documented as provenance; generated package content is incorporated. |
| B1 reproducibility package scripts | Synthetic demo and DSI benchmark runners | numpy, pandas, matplotlib | Included directly in `scripts/`. |

## Not found or not public-release-ready

- A standalone real-data 500-model Monte Carlo script independent of restricted
  input paths was not found. Public logic is provided in `monte_carlo.py`.
- A standalone figure script reproducing every manuscript panel from only public
  data was not found. The public repository includes synthetic figure support
  and corrected Fig. B5 outputs.
- Raw drillhole/trench parsing scripts were intentionally excluded because the
  raw data are restricted.
