import numpy as np
import pandas as pd


def get_representative_by_regions(
    df_regions: pd.DataFrame, n_representative: int, min_representative: int, method: str = "loreg"
) -> pd.DataFrame:
    """
    Función que devuelve el raprto de los escaños por regiones según el método especificado,
    el número total de representantes y el mínimo por region.

    Parameters
    ----------
    df_regions: pd.DataFrame
        Tabla con los datos de:
            - type_reg: "prov" si es provincia o "caut" si es ciudad autonoma.
            - size: Población total con derecho a voto.

    n_representative: int
        Número total de representantes
    min_representative: int
        Mínimo de representantes por provincias
    method: str
        Nombre del método de reparto. Por defecto utiliza el explicado en la LOREG

    Returns
    -------
    df_regions: pd.DataFrame
        DataFrame con el reparto de diputados por regiones
    """
    df_regions.insert(1, "n_rep", 1)

    method_formula = {
        "loreg": _distribution_loreg,
        "dhondt": _distribution_dhondt,
        "hare": _distribution_hare,
    }
    try:
        df_regions = method_formula[method](df_regions, n_representative, min_representative)
    except KeyError:
        raise RuntimeError(
            f"No existe el método {method}. " f"Elige el método {list(method_formula.keys())}."
        )
    df_regions = df_regions[["reg_el_id", "n_rep"]].sort_values("reg_el_id").reset_index(drop=True)
    return df_regions


def _distribution_loreg(
    regions: pd.DataFrame, n_representative: int, min_representative: int
) -> pd.DataFrame:
    """
    Función que distribuye los n_representative en las regiones de la tabla regions con un mínimo
    de min_representative según la LOREG
    http://www.juntaelectoralcentral.es/cs/jec/ley?idContenido=23758&p=1379062388933&template=Loreg/JEC_Contenido

    Parameters
    ----------
    regions: pd.DataFrame
        Tabla con las regiones y sus tamaños en población con derecho a voto.
    n_representative: int
        Número de representantes
    min_representative: int
        Mínimo de representantes.

    Returns
    -------
    regions: pd.DataFrame
        DataFrame con el reparto de diputados por regiones
    """
    mask_prov = regions.type_reg == "prov"
    regions.loc[mask_prov, "n_rep"] = min_representative
    rep_to_share = n_representative - regions.n_rep.sum()
    ratio_rep = regions.loc[mask_prov, "size"].sum() // rep_to_share
    cocient_rep = np.zeros(regions.shape[0])
    rest = np.zeros(regions.shape[0])
    cocient_rep[mask_prov] = (regions.loc[mask_prov, "size"] / ratio_rep).astype(int)
    rest[mask_prov] = regions.loc[mask_prov, "size"] / ratio_rep - cocient_rep[mask_prov]
    regions.loc[:, "n_rep"] += cocient_rep
    rep_to_share = n_representative - regions.n_rep.sum()
    regions = regions.loc[rest.argsort()[::-1]].reset_index(drop=True)
    for i in range(rep_to_share):
        regions.loc[i, "n_rep"] += 1
    return regions


def _distribution_dhondt(
    regions: pd.DataFrame, n_representative: int, min_representative: int
) -> pd.DataFrame:
    """
    Función que distribuye los n_representative en las regiones de la tabla regions con un mínimo
    de min_representative según la ley D'Hondt

    Parameters
    ----------
    regions: pd.DataFrame
        Tabla con las regiones y sus tamaños en población con derecho a voto.
    n_representative: int
        Número de representantes
    min_representative: int
        Mínimo de representantes.

    Returns
    -------
    regions: pd.DataFrame
        DataFrame con el reparto de diputados por regiones
    """
    regions = regions.sort_values("reg_el_id")
    mask_prov = regions.type_reg == "prov"
    regions.loc[mask_prov, "n_rep"] = min_representative
    rep_to_share = n_representative - regions.n_rep.sum()
    regions_s = regions[mask_prov].copy()
    regions_s["n_rep"] = 0
    regions_s.insert(regions_s.shape[1], "size_s", regions_s["size"].values)
    regions_s = regions_s.sort_values("size_s", ascending=False).reset_index(drop=True)
    for i in range(rep_to_share):
        regions_s.loc[0, "n_rep"] += 1
        regions_s.size_s = regions_s["size"] // (regions_s.n_rep + 1)
        regions_s = regions_s.sort_values("size_s", ascending=False).reset_index(drop=True)
    regions_s = regions_s.sort_values("reg_el_id")
    n_rep_values = regions.loc[mask_prov.values, "n_rep"] + regions_s["n_rep"].values
    regions.loc[mask_prov.values, "n_rep"] = n_rep_values
    return regions


def _distribution_hare(
    regions: pd.DataFrame, n_representative: int, min_representative: int
) -> pd.DataFrame:
    """
    Función que distribuye los n_representative en las regiones de la tabla regions con un mínimo
    de min_representative según el coeficiente de Hare.
    http://www.juntaelectoralcentral.es/cs/jec/ley?idContenido=23758&p=1379062388933&template=Loreg/JEC_Contenido

    Parameters
    ----------
    regions: pd.DataFrame
        Tabla con las regiones y sus tamaños en población con derecho a voto.
    n_representative: int
        Número de representantes
    min_representative: int
        Mínimo de representantes.

    Returns
    -------
    regions: pd.DataFrame
        DataFrame con el reparto de diputados por regiones
    """
    mask_prov = regions.type_reg == "prov"
    regions.loc[mask_prov, "n_rep"] = min_representative
    rep_to_share = n_representative - regions.n_rep.sum()
    regions = regions.sort_values("reg_el_id")
    regions_s = regions[mask_prov].copy()
    coeff_hare = regions_s["size"].sum() // rep_to_share
    regions_s["n_rep"] += regions_s["size"] // coeff_hare
    regions_s["size_s"] = regions_s["size"] - (regions_s.n_rep - min_representative) * coeff_hare
    regions_s = regions_s.sort_values("size_s", ascending=False).reset_index(drop=True)
    rest_n_rep = rep_to_share - regions_s.n_rep.sum()
    for i in range(rest_n_rep):
        regions_s.loc[i, "n_rep"] += 1
    regions[mask_prov] = regions_s.sort_values("reg_el_id")
    return regions
