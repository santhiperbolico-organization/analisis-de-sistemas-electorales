import numpy as np
import pandas as pd
import pytest

from electoral_system_analysis.distribution_regions import get_representative_by_regions


@pytest.fixture
def df_regions() -> pd.DataFrame:
    df_regions = pd.DataFrame(
        {
            "region": [
                "reg_0",
                "reg_1",
                "reg_2",
                "reg_3",
                "reg_4",
                "reg_5",
                "reg_6",
                "reg_7",
                "reg_8",
                "reg_9",
            ],
            "size": [
                5274869,
                4068343,
                2017012,
                1529713,
                1347870,
                1204201,
                1107536,
                989733,
                63301,
                61127,
            ],
        }
    )
    df_regions.index.name = "reg_el_id"
    df_regions.insert(2, "type_reg", "prov")
    df_regions.loc[[8, 9], "type_reg"] = "caut"
    return df_regions.reset_index()


@pytest.mark.parametrize(
    "method, n_representative, min_representative, expected",
    [
        ("loreg", 139, 2, np.array([38, 30, 16, 13, 11, 10, 10, 9, 1, 1])),
        ("loreg", 200, 1, np.array([58, 45, 23, 17, 16, 14, 13, 12, 1, 1])),
        ("dhondt", 20, 0, np.array([6, 5, 2, 1, 1, 1, 1, 1, 1, 1])),
        ("dhondt", 20, 1, np.array([5, 4, 2, 2, 2, 1, 1, 1, 1, 1])),
    ],
)
def test_get_representative_by_regions(
    df_regions, method, n_representative, min_representative, expected
):
    result = get_representative_by_regions(
        df_regions, n_representative, min_representative, method
    )
    assert (result.n_rep.values == expected).all()
