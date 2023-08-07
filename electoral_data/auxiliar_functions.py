import numpy as np
import pandas as pd


def format_serie_values(values: pd.Series) -> pd.Series:
    """
    Función que formatea una serie para que tenga un
    formato más amigable.

    Parameters
    ----------
    values: pd.Series
        Serie a formatear
    Returns
    -------
    values: pd.Series
        Serie formateada
    """
    values = values.str.lower().str.strip().str.replace(" ", "")
    values = values.str.replace(".", "_")
    values = values.str.replace("/", "_")
    tildes = {"á": "a", "è": "e", "é": "e", "í": "i", "ó": "o", "ú": "u"}
    for key, value in tildes.items():
        values = values.str.replace(key, value)
    return values
