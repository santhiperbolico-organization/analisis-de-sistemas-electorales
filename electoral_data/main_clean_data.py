from electoral_system_analysis.clean_electoral_data import clean_2019, read_data_2023

# Es necesario descargar este archivo de:
# https://resultados.generales23j.es/assets/files/congreso.pdf
PATH_2023 = "electoral_data/raw_data/2023_julio/congreso.pdf"

if __name__ == "__main__":
    _, _ = clean_2019("november")
    _, _ = clean_2019("april")
    result = read_data_2023(PATH_2023)
    print(result)
