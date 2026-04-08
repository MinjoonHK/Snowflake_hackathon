import pandas as pd


def apply_custom_index(
    df: pd.DataFrame,
    w_pop: int,
    w_visit: int,
    w_cons: int,
    w_div: int,
    w_inc: int,
    w_cred: int,
) -> None:
    total_w = w_pop + w_visit + w_cons + w_div + w_inc + w_cred
    if total_w > 0:
        df["CUSTOM_INDEX"] = (
            df["SCORE_POPULATION"] * (w_pop / total_w)
            + df["SCORE_VISITING"] * (w_visit / total_w)
            + df["SCORE_CONSUMPTION"] * (w_cons / total_w)
            + df["SCORE_DIVERSITY"] * (w_div / total_w)
            + df["SCORE_INCOME"] * (w_inc / total_w)
            + df["SCORE_CREDIT"] * (w_cred / total_w)
        ).round(2)
    else:
        df["CUSTOM_INDEX"] = df["VITALITY_INDEX"]
