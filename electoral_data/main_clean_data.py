from electoral_system_analysis.clean_electoral_data import (
    clean_2019,
    create_region_table_2019,
    read_data_2023,
    read_data_2023_rtve,
)

# Es necesario descargar este archivo de:
# https://resultados.generales23j.es/assets/files/congreso.pdf
PATH_2023 = "electoral_data/raw_data/2023_julio/congreso.pdf"
PATH_2019 = "electoral_data/raw_data/2019_noviembre/PROV_02_201911_1.xlsx"
PATH_2023_RTVE = "electoral_data/raw_data/2023_julio/Datos definitivos Elecciones 2023.xlsx"

PATH_TO_WRITE_2019 = "electoral_data/clean_data/2019_noviembre"
PATH_TO_WRITE_2023 = "electoral_data/clean_data/2023_julio"

if __name__ == "__main__":
    reg_2019, df_parties_2019 = clean_2019(PATH_2019, PATH_TO_WRITE_2019)
    df_regions_2019 = create_region_table_2019(PATH_2019, PATH_TO_WRITE_2019)
    df_pre_parties_2023 = read_data_2023(PATH_2023, PATH_TO_WRITE_2023)
    print(df_pre_parties_2023)

    data = read_data_2023_rtve(PATH_2023_RTVE)
    print(data)
