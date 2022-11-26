import logging

import numpy as np
import pandas as pd

from sqlalchemy import text

from groceries.db import models

logger = logging.getLogger(__name__)


def read_shopping_list(path):
    logger.debug(f"read shopping list: {path}")
    df_dict = pd.read_excel(path, sheet_name=None)

    df = pd.DataFrame()
    for store_name, df_store in df_dict.items():
        df_store["store"] = store_name
        df = pd.concat([df, df_store])

    return df


def get_shopping_list(sql_path, session):
    logger.debug("generate shopping list from database prices")

    with open(sql_path, "r") as f:
        sql = text(f.read())

    engine = session.get_bind()
    conn = engine.connect()
    df = pd.read_sql(sql, conn)

    # rename all columns to be lower-case
    df = df.rename(columns={c: c.lower() for c in df.columns})
    return df


def write_shopping_list(df, session, output_path=None):
    columns = df.columns.tolist()
    df = df.sort_values(by=columns)

    if output_path is not None:
        stores = session.query(models.Store).filter(models.Store.active == 1).all()
        store_names = [store.name for store in stores]
        with pd.ExcelWriter(output_path) as writer:
            for store_name in store_names:
                logger.debug(f"write shopping list for '{store_name}'")
                df[df["store"] == store_name][columns[1:]].to_excel(
                    writer, sheet_name=store_name, index=False
                )
    return df


def __price_diff(row):
    original = row["original_price"]
    updated = row["updated_price"]

    try:
        return updated - original
    except TypeError:
        return np.nan


def get_changed(df_original, df_updated):

    # add columns for tracking where the data came from after it is combined
    df_original["source"] = "original"
    df_updated["source"] = "updated"

    for column in ["store", "price"]:
        df_updated[f"updated_{column}"] = df_updated[column]
        df_original[f"original_{column}"] = df_original[column]

    # get a dataframe of all items that changed price or store
    df_changed = pd.concat([df_original, df_updated]).drop_duplicates(
        subset=["description", "store", "price"], keep=False
    )
    # create key columns that are kept in the final changed dataframe (after grouping)
    columns = ["category", "description"]
    for col in ["store", "price"]:
        columns.append(f"original_{col}")
        columns.append(f"updated_{col}")
    df_changed = df_changed[columns]
    if df_changed.empty:
        # the dataframe is empty, no need to combine columns
        return df_changed

    # Combine the rows so that each difference is represented as a single row
    df_changed = df_changed.fillna("")
    df_changed = df_changed.astype(str)
    df_changed = df_changed.groupby(by=["category", "description"]).agg("".join)

    # then keep only selected columns
    df_changed.reset_index(inplace=True)
    df_changed = df_changed[columns]

    # change the type for all price columns to numeric or nan
    for col in ["original", "updated"]:
        df_changed[f"{col}_price"] = pd.to_numeric(
            df_changed[f"{col}_price"], errors="coerce", downcast=None
        )

    # calculate the price difference between new and old prices, where applicable
    df_changed["price_difference"] = df_changed.apply(__price_diff, axis=1)
    return df_changed


def generate_shopping_list(output_path, changed_path, sql_path, session):

    df_updated = get_shopping_list(sql_path=sql_path, session=session)
    write_shopping_list(df_updated, session, output_path)
    try:
        df_original = read_shopping_list(output_path)

        df_changed = get_changed(df_original, df_updated)
        if df_changed is not None:
            df_changed.to_excel(changed_path, index=False)
    except FileNotFoundError:
        logger.info(
            f"original shopping list not found at: {output_path}\nno changes generated"
        )

    logger.info(f"generated shopping list at: {output_path}")
