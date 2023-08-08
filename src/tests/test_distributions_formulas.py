import numpy as np
import pandas as pd
import pytest

from electoral_system_analysis.distribution_formulas import (
    FormulaDosntExist,
    distributions_representative_by_regions,
    get_distribution_formula,
)


@pytest.fixture
def df_votes() -> pd.DataFrame:
    df_votes = pd.DataFrame(
        {
            "party": [
                "party_a",
                "party_b",
                "party_c",
                "party_d",
                "party_e",
                "party_f",
                "party_g",
                "party_a",
                "party_b",
                "party_c",
                "party_d",
                "party_e",
                "party_f",
                "party_g",
            ],
            "votes": [
                391000,
                311000,
                184000,
                73000,
                27000,
                12000,
                2000,
                200000,
                260000,
                80000,
                120000,
                0,
                23000,
                5000,
            ],
            "region": [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        }
    )
    return df_votes


@pytest.fixture
def df_regions() -> pd.DataFrame:
    df_regions = pd.DataFrame(
        {
            "reg_el_id": [0, 1],
            "n_rep": [21, 10],
        }
    )
    return df_regions


@pytest.mark.parametrize(
    "method, expected",
    [
        ("hare", np.array([8, 6, 4, 2, 1, 0, 0])),
        ("dhondt", np.array([9, 7, 4, 1, 0, 0, 0])),
        ("imperiali", np.array([9, 7, 4, 1, 0, 0, 0])),
        ("droop", np.array([8, 7, 4, 2, 0, 0, 0])),
        ("hagenbach", np.array([8, 7, 4, 2, 0, 0, 0])),
        ("sainte_lague", np.array([8, 6, 4, 2, 1, 0, 0])),
        ("sainte_lague_modificado", np.array([8, 7, 4, 2, 0, 0, 0])),
    ],
)
def test_formula_distribution(df_votes, df_regions, method, expected):
    formula = get_distribution_formula(method)
    result = formula(df_votes[df_votes.region == 0], expected.sum())
    assert (expected == result.n_rep.values).all()


def test_formula_dosnt_exist():
    with pytest.raises(FormulaDosntExist):
        get_distribution_formula("fake_method")


@pytest.mark.parametrize(
    "electoral_barrier, expected",
    [(0.0, np.array([11, 10, 5, 4, 1, 0, 0])), (0.08, np.array([12, 12, 5, 2, 0, 0, 0]))],
)
def test_distributions_representative_by_regions(
    df_votes, df_regions, electoral_barrier, expected
):
    method = "hare"
    result = distributions_representative_by_regions(
        method, df_votes, df_regions, electoral_barrier
    )
    assert (expected == result.n_rep.values).all()


def test_electoral_barrier_error(df_votes, df_regions):
    with pytest.raises(RuntimeError):
        _ = distributions_representative_by_regions("hare", df_votes, df_regions, 0.8)
