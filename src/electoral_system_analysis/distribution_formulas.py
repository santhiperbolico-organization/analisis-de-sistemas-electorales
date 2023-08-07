from typing import Callable

import pandas as pd


FormulaFunction = Callable[[pd.DataFrame, pd.DataFrame, float], pd.DataFrame]


class FormulaDosntExist(Exception):
    pass


def dhont_rule(
        votes: pd.DataFrame,
        regions: pd.DataFrame,
        electoral_barrier: float
) -> pd.DataFrame:
    """
    Función que aplica la distribución de escaños usando la ley D'Hont.

    Parameters
    ----------
    votes: pd.DataFrame
        Tabla con los votos por partido y regiones.
    regions: pd.DataFrame
        Tabla con el reparto de escaños por regiones.
    electoral_barrier: float
        Valor de la barrera electoral

    Returns
    -------
    df_rep: pd.DataFrame
        Tabla con el reparto de escaños por partído.
    """
    df_rep = votes.groupby("party").sum()[["votes"]]
    df_rep.insert(1, "n_rep", 0)
    for _, reg_row in regions.iterrows():
        votes_reg = votes[votes.region == reg_row["reg_el_id"]].copy()
        votes_reg = votes_reg[votes_reg.votes >= electoral_barrier * votes_reg.votes.sum()]
        votes_reg.insert(votes_reg.shape[1], "n_rep", 0)
        votes_reg.insert(votes_reg.shape[1], "vot_s", votes_reg.votes.values)
        votes_reg = votes_reg.sort_values("vot_s", ascending=False).reset_index(drop=True)
        for i in range(reg_row["n_rep"]):
            votes_reg.loc[0, "n_rep"] += 1
            votes_reg.vot_s = votes_reg.votes // (votes_reg.n_rep + 1)
            votes_reg = votes_reg.sort_values("vot_s", ascending=False).reset_index(drop=True)
        df_rep.loc[votes_reg.party, "n_rep"] += votes_reg["n_rep"].values
    df_rep = df_rep.sort_values("n_rep", ascending=False).reset_index()
    return df_rep


def sainte_lague(
        votes: pd.DataFrame,
        regions: pd.DataFrame,
        electoral_barrier: float
) -> pd.DataFrame:
    """
    Función que aplica la distribución de escaños usando la ley Sainte Lague.

    Parameters
    ----------
    votes: pd.DataFrame
        Tabla con los votos por partido y regiones.
    regions: pd.DataFrame
        Tabla con el reparto de escaños por regiones.
    electoral_barrier: float
        Valor de la barrera electoral

    Returns
    -------
    df_rep: pd.DataFrame
        Tabla con el reparto de escaños por partído.
    """
    df_rep = votes.groupby("party").sum()[["votes"]]
    df_rep.insert(1, "n_rep", 0)
    for _, reg_row in regions.iterrows():
        votes_reg = votes[votes.region == reg_row["reg_el_id"]].copy()
        votes_reg = votes_reg[votes_reg.votes >= electoral_barrier * votes_reg.votes.sum()]
        votes_reg.insert(votes_reg.shape[1], "n_rep", 0)
        votes_reg.insert(votes_reg.shape[1], "vot_s", votes_reg.votes.values)
        votes_reg = votes_reg.sort_values("vot_s", ascending=False).reset_index(drop=True)
        for i in range(reg_row["n_rep"]):
            votes_reg.loc[0, "n_rep"] += 1
            votes_reg.vot_s = votes_reg.votes // (2*votes_reg.n_rep + 1)
            votes_reg = votes_reg.sort_values("vot_s", ascending=False).reset_index(drop=True)
        df_rep.loc[votes_reg.party, "n_rep"] += votes_reg["n_rep"].values
    df_rep = df_rep.sort_values("n_rep", ascending=False).reset_index()
    return df_rep


def sainte_lague_modificado(
        votes: pd.DataFrame,
        regions: pd.DataFrame,
        electoral_barrier: float
) -> pd.DataFrame:
    """
    Función que aplica la distribución de escaños usando la ley Sainte Lague Modificado.

    Parameters
    ----------
    votes: pd.DataFrame
        Tabla con los votos por partido y regiones.
    regions: pd.DataFrame
        Tabla con el reparto de escaños por regiones.
    electoral_barrier: float
        Valor de la barrera electoral

    Returns
    -------
    df_rep: pd.DataFrame
        Tabla con el reparto de escaños por partído.
    """
    df_rep = votes.groupby("party").sum()[["votes"]]
    df_rep.insert(1, "n_rep", 0)
    for _, reg_row in regions.iterrows():
        votes_reg = votes[votes.region == reg_row["reg_el_id"]].copy()
        votes_reg = votes_reg[votes_reg.votes >= electoral_barrier * votes_reg.votes.sum()]
        votes_reg.insert(votes_reg.shape[1], "n_rep", 0)
        votes_reg.insert(votes_reg.shape[1], "vot_s", votes_reg.votes.values / 1.4)
        votes_reg = votes_reg.sort_values("vot_s", ascending=False).reset_index(drop=True)
        for i in range(reg_row["n_rep"]):
            votes_reg.loc[0, "n_rep"] += 1
            votes_reg.loc[0, "vot_s"] = votes_reg.loc[0, "votes"] // (2*votes_reg.loc[0, "n_rep"] + 1)
            votes_reg.vot_s = votes_reg.votes // (2*votes_reg.n_rep + 1)
            votes_reg = votes_reg.sort_values("vot_s", ascending=False).reset_index(drop=True)
        df_rep.loc[votes_reg.party, "n_rep"] += votes_reg["n_rep"].values
    df_rep = df_rep.sort_values("n_rep", ascending=False).reset_index()
    return df_rep


def hare_coefficient(
        votes: pd.DataFrame,
        regions: pd.DataFrame,
        electoral_barrier: float
) -> pd.DataFrame:
    """
    Función que aplica la distribución de escaños usando el coeficiente de Hare.

    Parameters
    ----------
    votes: pd.DataFrame
        Tabla con los votos por partido y regiones.
    regions: pd.DataFrame
        Tabla con el reparto de escaños por regiones.
    electoral_barrier: float
        Valor de la barrera electoral

    Returns
    -------
    df_rep: pd.DataFrame
        Tabla con el reparto de escaños por partído.
    """
    df_rep = votes.groupby("party").sum()[["votes"]]
    df_rep.insert(1, "n_rep", 0)
    for _, reg_row in regions.iterrows():
        votes_reg = votes[votes.region == reg_row["reg_el_id"]].copy()
        votes_reg = votes_reg[votes_reg.votes >= electoral_barrier * votes_reg.votes.sum()]
        coeff_hare = votes_reg.votes.sum() // reg_row["n_rep"]
        votes_reg.insert(votes_reg.shape[1], "n_rep", votes_reg.votes // coeff_hare)
        votes_reg.insert(votes_reg.shape[1], "rest_votes", votes_reg.votes - votes_reg.n_rep * coeff_hare)
        votes_reg = votes_reg.sort_values("rest_votes", ascending=False).reset_index(drop=True)
        rest_n_rep = reg_row["n_rep"] - votes_reg.n_rep.sum()
        for i in range(rest_n_rep):
            votes_reg.loc[i, "n_rep"] += 1
        df_rep.loc[votes_reg.party, "n_rep"] += votes_reg["n_rep"].values
    df_rep = df_rep.sort_values("n_rep", ascending=False).reset_index()
    return df_rep


def get_distribution_formula(formula_name: str) -> FormulaFunction:
    """
    Función que devuelve la formula de reparto de escaños correspondiente.

    Parameters
    ----------
    formula_name: str
        Nombre del método: dhondt, sainte_lague, sainte_lague_modificado, hare

    Returns
    -------
    formula: FormulaFunction
        Función con la método de distribución de escaños.

    """

    dic_methods = {
        "dhondt": dhont_rule,
        "sainte_lague": sainte_lague,
        "sainte_lague_modificado": sainte_lague_modificado,
        "hare": hare_coefficient
    }

    try:
        return dic_methods[formula_name]
    except KeyError:
        raise FormulaDosntExist(f"El método {formula_name} no existe. "
                                f"Prueba con {list(dic_methods.keys())}.")
