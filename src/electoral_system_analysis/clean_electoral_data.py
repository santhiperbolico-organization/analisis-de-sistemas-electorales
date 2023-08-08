from typing import Tuple

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


def create_region_table(path_2019_file: str = None) -> pd.DataFrame:
    """
    Función que crea la tabla de regiones sacada de la información de 2019.

    Parameters
    ----------
    path_2019_file: str, default None
        Ruta del archivo con los datos electorales de 2019 descargados desde
        https://infoelectoral.interior.gob.es/opencms/es/elecciones-celebradas/area-de-descargas/

    Returns
    -------
    region_table: pd.DataFrame
    """
    if path_2019_file is None:
        path_2019_file = "electoral_data/raw_data/2019_noviembre/PROV_02_201911_1.xlsx"

    region_table = pd.read_excel(path_2019_file, skiprows=5, skipfooter=2, usecols=[2])
    region_table.columns = ["name"]
    region_table.name = region_table.name.str.strip()
    region_table["codename"] = region_table.name.str.replace(" ", "")
    region_table.codename = format_serie_values(region_table.codename)
    region_table["type_reg"] = "prov"
    region_table.loc[region_table.codename.isin(["ceuta", "melilla"]), "type_reg"] = "caut"
    region_table = region_table.reset_index(names="id")
    return region_table


def clean_november_2019(
    path_file: str = None,
    bbdd_parties: str = None,
    bbdd_coalition: str = None,
    bbdd_cp_rel: str = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Función que limpia los datos electorales de las elecciones de noviembre de 2019.

    Parameters
    ----------
    path_file: str, default None
        Ruta del archivo con los datos electorales descargados desde
        https://infoelectoral.interior.gob.es/opencms/es/elecciones-celebradas/area-de-descargas/

    Returns
    -------
    df_region: pd.DataFrame
        Tabla con los datos censales de las circunscripciones.
    df_parties: pd.DataFrame
        Tabla con los datos de diputados y votos de los partidos.
    """
    election_id = 0
    if path_file is None:
        path_file = "electoral_data/raw_data/2019_noviembre/PROV_02_201911_1.xlsx"
    if bbdd_parties is None:
        bbdd_parties = "electoral_data/raw_data/2019_noviembre/bbdd_partidos.csv"
    if bbdd_coalition is None:
        bbdd_coalition = "electoral_data/raw_data/2019_noviembre/bbdd_coaliciones.csv"
    if bbdd_cp_rel is None:
        bbdd_cp_rel = "electoral_data/raw_data/2019_noviembre/bbdd_coaliciones_relaciones.csv"

    # Formateo de columnas
    raw_data = pd.read_excel(path_file, skiprows=3, skipfooter=2)
    political_parties = raw_data.loc[0].fillna(method="ffill")
    header = raw_data.loc[1]
    header[~political_parties.isna()] = (
        political_parties[~political_parties.isna()] + "_" + header[~political_parties.isna()]
    )
    # Creación de las regiones.
    raw_data = raw_data.loc[2:]
    raw_data.columns = header.values
    diputados_cols = [c for c in raw_data.columns if "_Diputados" in c]
    raw_data["Diputados"] = raw_data[diputados_cols].sum(1)
    regions_raw_data = raw_data[["Nombre de Provincia", "Total censo electoral", "Diputados"]]
    regions_raw_data.columns = ["codename", "size", "n_representative"]
    regions_raw_data["election_id"] = election_id
    regions_raw_data.loc[:, "codename"] = format_serie_values(regions_raw_data.codename)

    # Carga de los votos.
    columns_votes = [c for c in raw_data.columns if "_Votos" in c]
    clean_data_votes = raw_data[["Nombre de Provincia"] + columns_votes].rename(
        columns={"Nombre de Provincia": "codename"}
    )
    clean_data_votes.loc[:, "codename"] = format_serie_values(clean_data_votes.codename)
    clean_data_votes[columns_votes] = clean_data_votes[columns_votes].astype(int)
    clean_data_votes.columns = clean_data_votes.columns.str.replace("_Votos", "")
    clean_data_votes = pd.melt(
        clean_data_votes, id_vars=["codename"], value_name="votes", var_name="political_parties"
    )
    clean_data_votes["election_id"] = election_id
    return regions_raw_data, clean_data_votes
