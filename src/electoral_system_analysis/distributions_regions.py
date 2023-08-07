import numpy as np
import pandas as pd


def get_representative_by_regions(
        df_regions: pd.DataFrame,
        n_representative: int,
        min_representative: int
) -> pd.DataFrame:
    df_regions.insert(1, "n_rep", 1)
    mask_prov = df_regions.type_reg == "prov"
    df_regions.loc[mask_prov, "n_rep"] = min_representative
    while df_regions["n_rep"].sum() < n_representative:
        df_regions = _distribution_loreg(df_regions, n_representative)
        mask_reg_with_rep = df_regions["n_rep"] == 0
        if mask_reg_with_rep.any():
            df_regions.loc[mask_prov, "n_rep"] = min_representative
            mask_reg_with_rep = df_regions["n_rep"] == 1
            df_regions.loc[mask_reg_with_rep, "n_rep"] = 1
    df_regions = df_regions[["reg_el_id", "n_rep"]].sort_values("reg_el_id").reset_index(drop=True)
    return df_regions


def _distribution_loreg(regions: pd.DataFrame, n_representative: int) -> pd.DataFrame:
    mask_prov = regions.type_reg == "prov"
    rep_to_share = n_representative - regions.n_rep.sum()
    ratio_rep = regions.loc[mask_prov, "size"].sum() / rep_to_share
    cocient = np.zeros(regions.shape[0])
    rest = np.zeros(regions.shape[0])
    cocient[mask_prov] = (regions.loc[mask_prov, "size"] / ratio_rep).astype(int)
    rest[mask_prov] = regions.loc[mask_prov, "size"] / ratio_rep - cocient[mask_prov]
    regions.loc[:, "n_rep"] += cocient
    rep_to_share = n_representative - regions.n_rep.sum()
    regions = regions.loc[rest.argsort()[::-1]].reset_index(drop=True)
    for i in range(rep_to_share):
        regions.loc[i, "n_rep"] += 1
    return regions
