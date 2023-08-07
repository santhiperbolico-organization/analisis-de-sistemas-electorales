from datetime import datetime
from typing import Tuple

import django
import pandas as pd

django.setup()

from electoral_law.electoral_data.auxiliar_functions import format_serie_values
from electoral_law.models import Election, Region, RegionElection, PoliticalParty, CoalitionPoliticalParty, CoalitionPartyRelation, VotesToPoliticalParty


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
        bbdd_cp_rel: str = None
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
    date = datetime.strptime("2019-11-10", "%Y-%m-%d")
    election = Election.objects.filter(date=date)[0]
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
    header[~political_parties.isna()] = political_parties[~political_parties.isna()] + "_" + \
                                        header[~political_parties.isna()]
    # Creación de las regiones.
    raw_data = raw_data.loc[2:]
    raw_data.columns = header.values
    diputados_cols = [c for c in raw_data.columns if "_Diputados" in c]
    raw_data["Diputados"] = raw_data[diputados_cols].sum(1)
    regions_raw_data = raw_data[["Nombre de Provincia", 'Total censo electoral', "Diputados"]]
    regions_raw_data.columns = ["codename", "size", "n_representative"]
    regions_raw_data["election_id"] = election.id
    regions_raw_data.loc[:, "codename"] = format_serie_values(regions_raw_data.codename)
    create_regions_elections(regions_raw_data)

    #Creación de los partidos, coaliciones y relaciones.
    create_political_parties(bbdd_parties)
    create_coalitions(bbdd_coalition)
    create_coalitions_relation(bbdd_cp_rel)

    # Carga de los votos.
    columns_votes = [c for c in raw_data.columns if "_Votos" in c]
    clean_data_votes = raw_data[["Nombre de Provincia"] + columns_votes].rename(
        columns={"Nombre de Provincia": "codename"})
    clean_data_votes.loc[:, "codename"] = format_serie_values(clean_data_votes.codename)
    clean_data_votes[columns_votes] = clean_data_votes[columns_votes].astype(int)
    clean_data_votes.columns = clean_data_votes.columns.str.replace("_Votos", "")
    clean_data_votes = pd.melt(clean_data_votes, id_vars=["codename"], value_name="votes",
            var_name="political_parties")
    clean_data_votes["election_id"] = election.id
    create_votes_to_political_party(clean_data_votes)
    return regions_raw_data, clean_data_votes


def create_regions_elections(regions_raw_data: pd.DataFrame) -> None:
    """
    Función que dada una tabla con el codename, size, n_representative y election_id
    genera los objetos RegionElection correspondientes, buscando con codename el
    region_id asociado.

    Parameters
    ----------
    regions_raw_data: pd.DataFrame
        Tabla con las columnas ["codename", "size", "n_representative", "election_id"]
    """
    for i, row in regions_raw_data.iterrows():
        region = Region.objects.filter(codename=row.codename)[0]
        region_election, exist = RegionElection.objects.get_or_create(
            size=row["size"],
            election_id=row["election_id"],
            region_id=region.id,
            n_representative=row["n_representative"]
        )
        region_election.save()


def create_political_parties(bbdd_data: str) -> None:
    """
    Fucnión que dada una ruta de un archivo csv crea los partidos políticos asociados
    si no existen en la base de datos.

    Parameters
    ----------
    bbdd_data: str
        Ruta del archivo de la base de datos
    """
    bbdd_pp = pd.read_csv(bbdd_data)
    for i, row in bbdd_pp.iterrows():
        party, _ = PoliticalParty.objects.get_or_create(
            name=row["name"],
            initialis=row["initialis"],
            color_pp=row["color_pp"]
        )
        party.save()


def create_coalitions(bbdd_data: str) -> None:
    """
    Fucnión que dada una ruta de un archivo csv crea coaliciones de partidos políticos asociados
    si no existen en la base de datos.

    Parameters
    ----------
    bbdd_data: str
        Ruta del archivo de la base de datos
    """
    bbdd_pp = pd.read_csv(bbdd_data)
    for i, row in bbdd_pp.iterrows():
        coalition, _ = CoalitionPoliticalParty.objects.get_or_create(
            name=row["name"],
            initialis=row["initialis"],
            color_cp=row["color_cp"],
            election_id=row["election_id"],
        )
        coalition.save()


def create_coalitions_relation(bbdd_data: str) -> None:
    """
    Fucnión que dada una ruta de un archivo csv crea las relaciones de las coaliciones y
    partidos políticos.

    Parameters
    ----------
    bbdd_data: str
        Ruta del archivo de la base de datos
    """
    bbdd_pp = pd.read_csv(bbdd_data)
    for i, row in bbdd_pp.iterrows():
        coalition, _ = CoalitionPartyRelation.objects.get_or_create(
            coalition_id=row["coalition_id"],
            political_party_id=row["political_party_id"]
        )
        coalition.save()


def create_votes_to_political_party(votes_to_parties: pd.DataFrame) -> None:
    """
    Función que guarda las votaciones registradas en la tabla votes_to_parties.
    La tabla ha de tener las columnas:
        * codename: Nombre formateado de la circunscripción.
        * political_parties: Iniciales del partido.
        * votes: Número de votos.
        * election_id: ID de las elecciones.

    Parameters
    ----------
    votes_to_parties: pd.DataFrame
        Tabla con las votaciones.
    """
    for i, row in votes_to_parties.iterrows():
        region = Region.objects.filter(codename=row.codename)[0]
        party = PoliticalParty.objects.filter(initialis=row.political_parties)[0]
        region_election = RegionElection.objects.filter(
            region_id=region.id, election_id=row.election_id)[0]
        votes, _ = VotesToPoliticalParty.objects.get_or_create(
            votes=row.votes,
            pp_id=party.id,
            region_election_id=region_election.id
        )
        votes.save()
