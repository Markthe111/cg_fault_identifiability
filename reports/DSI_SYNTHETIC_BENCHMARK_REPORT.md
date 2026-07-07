# DSI synthetic benchmark report

        - Result type: `SYNTHETIC_BENCHMARK_RESULT`
        - Random seed base: `20260705`
        - Configurations: `5 fault separations x 5 domain distances x 4 perturbation levels x 3 competing-fault counts x 3 domain-noise levels`
        - Replicates per configuration: `20`
        - Monte Carlo perturbations per replicate: `200`
        - Raw benchmark rows: `18000`
        - Spearman correlation between median DSI and reversal probability: `-0.759`

        ## Answers

        1. DSI and Monte Carlo reversal probability show a clear negative monotonic relationship in this controlled benchmark.
        2. High DSI cases are usually stable; benchmark bins are reported in `DSI_OPERATING_REGIONS.csv`.
        3. DSI close to one is boundary-sensitive and frequently unresolved.
        4. Threshold behavior depends on perturbation intensity, competing-fault count, and domain scatter.
        5. High-DSI failures occur mainly under extreme perturbation or added competing faults.
        6. Low-DSI stable exceptions occur where perturbation is low and point scatter is small.
        7. The benchmark supports DSI as a transferable pre-screening diagnostic, not as a guarantee.
        8. It cannot support a universal geological threshold or cross-deposit law without further calibration.

        ## Operating-region table

        ```json
        [
  {
    "dsi_bin": "ATTRIBUTION_UNRESOLVED",
    "count": 9673,
    "mean": 0.9520174713118991,
    "median": 1.0,
    "max": 1.0
  },
  {
    "dsi_bin": "BOUNDARY_SENSITIVE",
    "count": 815,
    "mean": 0.7076932515337423,
    "median": 0.85,
    "max": 1.0
  },
  {
    "dsi_bin": "MODERATE_MARGIN_CONDITIONAL",
    "count": 2305,
    "mean": 0.37182646420824295,
    "median": 0.21,
    "max": 1.0
  },
  {
    "dsi_bin": "HIGH_MARGIN_STABLE",
    "count": 5207,
    "mean": 0.13340791242558095,
    "median": 0.0,
    "max": 1.0
  }
]
        ```
