from electoral_law.auxiliar_functions import get_representative_distribution, get_parliament_chart_data, score_proportionality

if __name__ == "__main__":
    df_rep = get_representative_distribution(0)

    parliament_data = get_parliament_chart_data(df_rep)
    print(score_proportionality(df_rep.n_rep, df_rep.votes) * 100)

