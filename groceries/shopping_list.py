import pandas as pd

from sqlalchemy import text

from groceries.db import models


def read_shopping_list(path):

    df_dict = pd.read_excel(path, sheet_name=None)

    df = pd.DataFrame()
    for store_name, df_store in df_dict.items():
        df_store["store"] = store_name
        df = pd.concat([df, df_store])

    return df


def get_shopping_list(sql_path, session):

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
                df[df["store"] == store_name][columns[1:]].to_excel(
                    writer, sheet_name=store_name, index=False
                )
    return df


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
    return df_changed


def generate_shopping_list(output_path, changed_path, sql_path, session):

    update_changed = True
    try:
        df_original = read_shopping_list(output_path)
    except FileNotFoundError:
        update_changed = False

    df_updated = get_shopping_list(sql_path=sql_path, session=session)
    write_shopping_list(df_updated, session, output_path)

    if update_changed:
        df_changed = get_changed(df_original, df_updated)
        if df_changed is not None:
            df_changed.to_excel(changed_path, index=False)
