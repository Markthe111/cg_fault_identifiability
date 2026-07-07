"""Variance-component helper with statsmodels MixedLM and fallback."""
import numpy as np

def estimate_variance_components(residual_table, group_col):
    """Estimate inter-group and residual variance components; fallback to group-mean decomposition."""
    try:
        import statsmodels.formula.api as smf
        df = residual_table.copy()
        df["intercept"] = 1.0
        model = smf.mixedlm("residual ~ 1", df, groups=df[group_col])
        fit = model.fit(reml=True, disp=False)
        sigma_b = float(np.sqrt(max(fit.cov_re.iloc[0, 0], 0)))
        sigma_e = float(np.sqrt(max(fit.scale, 0)))
        return {"sigma_b": sigma_b, "sigma_e": sigma_e, "method": "MixedLM_REML", "converged": bool(fit.converged)}
    except Exception:
        df = residual_table.copy()
        means = df.groupby(group_col)["residual"].mean()
        sigma_b = float(means.std(ddof=1)) if len(means) > 1 else 0.0
        sigma_e = float(df.groupby(group_col)["residual"].std().mean())
        return {"sigma_b": sigma_b, "sigma_e": sigma_e, "method": "FALLBACK_GROUP_DECOMPOSITION", "converged": False}
