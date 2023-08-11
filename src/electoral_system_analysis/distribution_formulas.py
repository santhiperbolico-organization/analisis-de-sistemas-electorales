from typing import Callable

import numpy as np
import pandas as pd

FormulaFunction = Callable[[pd.DataFrame, int], pd.DataFrame]


class FormulaDosntExist(Exception):
    pass


def dhont_rule(votes: pd.DataFrame, total_rep: int) -> pd.DataFrame:
    """
    Función que aplica la distribución de escaños usando la ley D'Hont.

    Parameters
    ----------
    votes: pd.DataFrame
        Tabla con los votos por partido y regiones.

    total_rep: int
        Número total d eescaños a repartir.

    Returns
    -------
    votes_rep: pd.DataFrame
        Tabla de votos con la columna n_rep con los representantes repartidos.
    """
    votes_rep = votes.copy()
    votes_rep["n_rep"] = 0
    votes_rep.insert(votes_rep.shape[1], "vot_s", votes_rep.votes.values)
    votes_rep = votes_rep.sort_values("vot_s", ascending=False).reset_index(drop=True)
    for i in range(total_rep):
        votes_rep.loc[0, "n_rep"] += 1
        votes_rep.vot_s = votes_rep.votes // (votes_rep.n_rep + 1)
        votes_rep = votes_rep.sort_values("vot_s", ascending=False).reset_index(drop=True)
    votes_rep = votes_rep.set_index("party").loc[votes.party].reset_index()
    return votes_rep


def sainte_lague(votes: pd.DataFrame, total_rep: int) -> pd.DataFrame:
    """
    Función que aplica la distribución de escaños usando la ley Sainte Lague.

    Parameters
    ----------
    votes: pd.DataFrame
        Tabla con los votos por partido y regiones.

    total_rep: int
        Número total d eescaños a repartir.

    Returns
    -------
    votes_rep: pd.DataFrame
        Tabla de votos con la columna n_rep con los representantes repartidos.
    """
    votes_rep = votes.copy()
    votes_rep["n_rep"] = 0
    votes_rep.insert(votes_rep.shape[1], "vot_s", votes_rep.votes.values)
    votes_rep = votes_rep.sort_values("vot_s", ascending=False).reset_index(drop=True)
    for i in range(total_rep):
        votes_rep.loc[0, "n_rep"] += 1
        votes_rep.vot_s = votes_rep.votes // (2 * votes_rep.n_rep + 1)
        votes_rep = votes_rep.sort_values("vot_s", ascending=False).reset_index(drop=True)
    votes_rep = votes_rep.set_index("party").loc[votes.party].reset_index()
    return votes_rep


def sainte_lague_modificado(votes: pd.DataFrame, total_rep: int) -> pd.DataFrame:
    """
    Función que aplica la distribución de escaños usando la ley Sainte Lague Modificado.

    Parameters
    ----------
    votes: pd.DataFrame
        Tabla con los votos por partido y regiones.

    total_rep: int
        Número total d eescaños a repartir.

    Returns
    -------
    votes_rep: pd.DataFrame
        Tabla de votos con la columna n_rep con los representantes repartidos.
    """

    votes_rep = votes.copy()
    votes_rep["n_rep"] = 0
    votes_rep.insert(votes_rep.shape[1], "vot_s", votes_rep.votes.values / 1.4)
    votes_rep = votes_rep.sort_values("vot_s", ascending=False).reset_index(drop=True)
    for i in range(total_rep):
        votes_rep.loc[0, "n_rep"] += 1
        votes_rep.loc[0, "vot_s"] = votes_rep.loc[0, "votes"] // (
            2 * votes_rep.loc[0, "n_rep"] + 1
        )
        votes_rep = votes_rep.sort_values("vot_s", ascending=False).reset_index(drop=True)
    votes_rep = votes_rep.set_index("party").loc[votes.party].reset_index()
    return votes_rep


def hare_coefficient(votes: pd.DataFrame, total_rep: int) -> pd.DataFrame:
    """
    Función que aplica la distribución de escaños usando el coeficiente de Hare.

    Parameters
    ----------
    votes: pd.DataFrame
        Tabla con los votos por partido y regiones.

    total_rep: int
        Número total d eescaños a repartir.

    Returns
    -------
    votes_rep: pd.DataFrame
        Tabla de votos con la columna n_rep con los representantes repartidos.
    """
    votes_rep = votes.copy()
    coeff_hare = votes_rep.votes.sum() // total_rep
    votes_rep["n_rep"] = votes_rep.votes // coeff_hare
    votes_rep.insert(
        votes_rep.shape[1], "rest_votes", votes_rep.votes - votes_rep.n_rep * coeff_hare
    )
    votes_rep = votes_rep.sort_values("rest_votes", ascending=False).reset_index(drop=True)
    rest_n_rep = total_rep - votes_rep.n_rep.sum()
    for i in range(rest_n_rep):
        votes_rep.loc[i, "n_rep"] += 1
    votes_rep = votes_rep.set_index("party").loc[votes.party].reset_index()
    return votes_rep


def droop_coefficient(votes: pd.DataFrame, total_rep: int) -> pd.DataFrame:
    """
    Función que aplica la distribución de escaños usando el coeficiente de Droop.

    Parameters
    ----------
    votes: pd.DataFrame
        Tabla con los votos por partido y regiones.

    total_rep: int
        Número total d eescaños a repartir.

    Returns
    -------
    votes_rep: pd.DataFrame
        Tabla de votos con la columna n_rep con los representantes repartidos.
    """

    votes_rep = votes.copy()
    coeff_droop = 1 + votes_rep.votes.sum() // (total_rep + 1)
    votes_rep["n_rep"] = votes_rep.votes // coeff_droop
    votes_rep.insert(
        votes_rep.shape[1], "rest_votes", votes_rep.votes - votes_rep.n_rep * coeff_droop
    )
    votes_rep = votes_rep.sort_values("rest_votes", ascending=False).reset_index(drop=True)
    rest_n_rep = total_rep - votes_rep.n_rep.sum()
    for i in range(rest_n_rep):
        votes_rep.loc[i, "n_rep"] += 1
    votes_rep = votes_rep.set_index("party").loc[votes.party].reset_index()
    return votes_rep


def hagenbach_coefficient(votes: pd.DataFrame, total_rep: int) -> pd.DataFrame:
    """
    Función que aplica la distribución de escaños usando el coeficiente de Hagenbach-Bischoff.

    Parameters
    ----------
    votes: pd.DataFrame
        Tabla con los votos por partido y regiones.

    total_rep: int
        Número total d eescaños a repartir.

    Returns
    -------
    votes_rep: pd.DataFrame
        Tabla de votos con la columna n_rep con los representantes repartidos.
    """
    votes_rep = votes.copy()
    coeff_hagenbach = votes_rep.votes.sum() // (total_rep + 1)
    votes_rep["n_rep"] = votes_rep.votes // coeff_hagenbach
    votes_rep.insert(
        votes_rep.shape[1], "rest_votes", votes_rep.votes - votes_rep.n_rep * coeff_hagenbach
    )
    votes_rep = votes_rep.sort_values("rest_votes", ascending=False).reset_index(drop=True)
    rest_n_rep = total_rep - votes_rep.n_rep.sum()
    for i in range(rest_n_rep):
        votes_rep.loc[i, "n_rep"] += 1
    votes_rep = votes_rep.set_index("party").loc[votes.party].reset_index()
    return votes_rep


def imperiali_coefficient(votes: pd.DataFrame, total_rep: int) -> pd.DataFrame:
    """
    Función que aplica la distribución de escaños usando el coeficiente de Imperiali.

    Parameters
    ----------
    votes: pd.DataFrame
        Tabla con los votos por partido y regiones.

    total_rep: int
        Número total d eescaños a repartir.

    Returns
    -------
    votes_rep: pd.DataFrame
        Tabla de votos con la columna n_rep con los representantes repartidos.
    """
    votes_rep = votes.copy()
    coeff_imperiali = votes_rep.votes.sum() // (total_rep + 2)
    votes_rep["n_rep"] = votes_rep.votes // coeff_imperiali
    votes_rep.insert(
        votes_rep.shape[1], "rest_votes", votes_rep.votes - votes_rep.n_rep * coeff_imperiali
    )
    votes_rep = votes_rep.sort_values("rest_votes", ascending=False).reset_index(drop=True)
    rest_n_rep = total_rep - votes_rep.n_rep.sum()
    for i in range(rest_n_rep):
        votes_rep.loc[i, "n_rep"] += 1
    votes_rep = votes_rep.set_index("party").loc[votes.party].reset_index()
    return votes_rep


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
        "hare": hare_coefficient,
        "imperiali": imperiali_coefficient,
        "droop": droop_coefficient,
        "hagenbach": hagenbach_coefficient,
    }

    try:
        return dic_methods[formula_name]
    except KeyError:
        raise FormulaDosntExist(
            f"El método {formula_name} no existe. " f"Prueba con {list(dic_methods.keys())}."
        )


def distributions_representative_by_regions(
    formula_name: str, votes: pd.DataFrame, regions: pd.DataFrame, electoral_barrier: float
) -> pd.DataFrame:
    """
    Función que aplica la distribución de escaños usando la ley D'Hont.

    Parameters
    ----------
    formula_name: str
        Nombre de la fórmula de cálculo del reparto.
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
    fomula_method = get_distribution_formula(formula_name)
    for _, reg_row in regions.iterrows():
        votes_reg = votes[votes.region == reg_row["reg_el_id"]].copy()
        votes_reg = votes_reg[votes_reg.votes >= electoral_barrier * votes_reg.votes.sum()]
        if len(votes_reg) == 0:
            raise RuntimeError(
                f"No hay votos para ningún partido en esta región que hayan "
                f"superado la barrera electoral de {electoral_barrier*100} %."
            )
        votes_reg = fomula_method(votes_reg, reg_row["n_rep"])
        df_rep.loc[votes_reg.party, "n_rep"] += votes_reg["n_rep"].values
    df_rep = df_rep.sort_values("n_rep", ascending=False).reset_index()
    return df_rep


def score_proportionality(representative: pd.Series, votes: pd.Series) -> float:
    """
    Función que calcula un score de representatividad como 1 menos la media de la diferencia
    absoluta entre el porcentaje de diputados y el porcentaje de votos.

    Parameters
    ----------
    representative: pd.Series
        Serie con los diputados por partido.
    votes: pd.Series
        Serie con los votos por partido.

    Returns
    -------
    score: float
        Valor asociado a la proporcionalidad, donde 1 es una proporcionalidad absoluta
        y 0 una autocracia.
            Score = 1 - Mean(|representative_percent - votes_percent|)
    """
    representative_percent = representative / representative.sum()
    votes_percent = votes / votes.sum()
    error_abs = np.abs(representative_percent - votes_percent)
    return 1 - np.sum(error_abs)
