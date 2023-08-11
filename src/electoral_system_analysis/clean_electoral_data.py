import os
import re
from typing import List, Tuple

import pandas as pd
from pypdf import PdfReader


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


def create_region_table_2019(file_2019: str, path_to_write: str) -> pd.DataFrame:
    """
    Función que crea la tabla de regiones sacada de la información de 2019.

    Parameters
    ----------
    file_2019: str, default None
        Ruta del archivo con los datos electorales de 2019 descargados desde
        https://infoelectoral.interior.gob.es/opencms/es/elecciones-celebradas/area-de-descargas/

    path_to_write: str
        Ruta donde se quiere guardar los resultados.

    Returns
    -------
    region_table: pd.DataFrame
        Tabla con la información de las regiones.
    """
    region_table = pd.read_excel(file_2019, skiprows=5, skipfooter=2, usecols=[2])
    region_table.columns = ["name"]
    region_table.name = region_table.name.str.strip()
    region_table["codename"] = format_serie_values(region_table.name)
    region_table["type_reg"] = "prov"
    region_table.loc[region_table.codename.isin(["ceuta", "melilla"]), "type_reg"] = "caut"
    region_table = region_table.reset_index(names="id")
    region_table.to_csv(os.path.join(path_to_write, "region_table_2019.csv"))
    return region_table


def clean_2019(file_2019: str, path_to_write: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Función que limpia los datos electorales de las elecciones generales de 2019
    ( tanto de abril y noviembre). Los datos electorales descargados desde:
    https://infoelectoral.interior.gob.es/opencms/es/elecciones-celebradas/area-de-descargas/

    Parameters
    ----------
    file_2019: str, default None
        Ruta del archivo con los datos electorales de 2019 descargados desde
        https://infoelectoral.interior.gob.es/opencms/es/elecciones-celebradas/area-de-descargas/

    path_to_write: str
        Ruta donde se quiere guardar los resultados.

    Returns
    -------
    df_region: pd.DataFrame
        Tabla con los datos censales de las circunscripciones.
    df_parties: pd.DataFrame
        Tabla con los datos de diputados y votos de los partidos.
    """

    # Formateo de columnas
    raw_data = pd.read_excel(file_2019, skiprows=3, skipfooter=2)
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
    df_region = raw_data[["Nombre de Provincia", "Total censo electoral", "Diputados"]]
    df_region.columns = ["codename", "size", "n_representative"]
    df_region.loc[:, "codename"] = format_serie_values(df_region.codename)

    # Carga de los votos.
    columns_votes = [c for c in raw_data.columns if "_Votos" in c]
    df_parties = raw_data[["Nombre de Provincia"] + columns_votes].rename(
        columns={"Nombre de Provincia": "codename"}
    )
    df_parties.loc[:, "codename"] = format_serie_values(df_parties.codename)
    df_parties[columns_votes] = df_parties[columns_votes].astype(int)
    df_parties.columns = df_parties.columns.str.replace("_Votos", "")
    df_parties = pd.melt(
        df_parties, id_vars=["codename"], value_name="votes", var_name="political_parties"
    )

    if not os.path.exists(path_to_write):
        os.mkdir(path_to_write)

    df_region.to_csv(os.path.join(path_to_write, "regions_raw_data.csv"))
    df_parties.to_csv(os.path.join(path_to_write, "clean_data_votes.csv"))
    return df_region, df_parties


def read_data_2023(path: str, path_to_write: str) -> pd.DataFrame:
    """
    Función que lee los datos electorales de julio de 2023 de un pdf y los convierte a
    tabla:
    https://resultados.generales23j.es/assets/files/congreso.pdf
    La función recorre los datos por provincias del documento. El resultado final
    tiene datos de las elecciones de 2019 que se necesitan limpiar a mano.

    Parameters
    ----------
    path: str
        Ruta del archivo congreso.pdf descargado de:
        https://resultados.generales23j.es/assets/files/congreso.pdf

    path_to_write: str
        Ruta donde se quiere guardar los resultados.

    Returns
    -------
    result: pd.DataFrame
        Tabla con el documento formateado
    """
    reader = PdfReader(path)
    number_of_pages = len(reader.pages)
    start_page = 45  # Donde empiezan los datos de provincias.
    result = pd.DataFrame(
        {},
        columns=["region", "total_votes", "valid_votes", "cand_votes", "party_initialis", "votes"],
    )

    for n_page in range(start_page, number_of_pages):
        page = reader.pages[n_page]
        text = page.extract_text().split("\n")
        result_reg = format_pdf_data_2023(text)
        result = pd.concat((result, result_reg)).reset_index(drop=True)

    result.to_csv(os.path.join(path_to_write, "pre_clean_congreso.csv"))
    return result


def format_pdf_data_2023(text: List[str]) -> pd.DataFrame:
    """
    Función que formatea las páginas de los datos provisionales de las elecciones generales
    de 2023 https://resultados.generales23j.es/assets/files/congreso.pdf. Para ello se apoya
    en el formato estandar de cada página

    Parameters
    ----------
    text: List[str]
        Lista con las líneas de una página del informe.

    Returns
    -------
    result: pd.DataFrame
        Tabla con la página formateado

    """
    result = pd.DataFrame(
        {},
        columns=["region", "total_votes", "valid_votes", "cand_votes", "party_initialis", "votes"],
    )
    region_name = "Unknown"
    total_votes = 0
    valid_votes = 0
    cand_votes = 0
    k_candidaturas = 0
    for line in text:
        if re.match("^España .* Congreso", line):
            region_name = line.replace("España", "").replace("Congreso", "").strip()
        elif re.match("^participación.*", line.lower()):
            total_votes = int(line.strip().split(" ")[1].replace(".", "").replace(",", "."))
        elif re.match("^votos válidos.*", line.lower()):
            valid_votes = int(line.strip().split(" ")[2].replace(".", "").replace(",", "."))
        elif re.match("^a candidatura.*", line.lower()):
            cand_votes = int(line.strip().split(" ")[2].replace(".", "").replace(",", "."))
        elif re.match("^candidaturas.*", line.lower()):
            break
        k_candidaturas += 1

    index_row = 0
    firs_part_name = ""

    for k in range(k_candidaturas + 1, len(text)):
        line = text[k]
        row_party_name = re.split("\d", line)[0]
        if row_party_name == "":
            row_party_name = re.split(" ", line)[0]
        party_name = firs_part_name + row_party_name
        data = line.split(row_party_name)[1]
        if data == "":
            firs_part_name = party_name
        else:
            party_name = party_name.strip()
            clean_data = re.sub("[+-]( )?\d", "", data).split(" ")
            votes = int(clean_data[1].replace(".", ""))
            if votes == 0:  # No hay datos de partidos con 0 votos.
                votes = int(clean_data[2].replace(".", ""))
            result.loc[index_row, :] = [
                region_name,
                total_votes,
                valid_votes,
                cand_votes,
                party_name,
                votes,
            ]
            index_row += 1
            firs_part_name = ""

    return result
