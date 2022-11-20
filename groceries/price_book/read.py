import numpy as np
import pandas as pd

from groceries.db import models


def __get_prices_to_delete(df):
    # get all Price objects where the price is blank
    missing_price_df = df[(np.isnan(df["price2"])) & (df["Price"].notnull())]["Price"]

    missing_price_df["price_id"] = df["Price"].apply(
        lambda x: None if x is None else x.price_id
    )
    print(missing_price_df.to_string())
    print(df.head(15).to_string())


def __parse_price(price, preference_types):
    pt = preference_types.get(price)
    if isinstance(price, str):
        price = np.nan
    if pt is None:
        pt = preference_types.get("S")
    return pt, price


def __update_preferred_store(row):
    item = row["Item"]
    pref_store = row["pref_store"]

    item.preferred_store = pref_store
    return item


def __update_item(row):
    item = row["Item"]

    # reminder, do not update the description column because the description in the
    # price book is formatted with units!
    category = row["Category"]
    pref_store = row["pref_Store"]
    # description = row['description']

    item.category = category
    item.preferred_store = pref_store
    # item.description = description
    return item


def __update_price(row, preference_types=None):
    price = row["Price"]
    if price is None:
        return None

    pt, price_val = __parse_price(row["price"], preference_types)

    try:
        price_val = float(price_val)
    except ValueError:
        price_val = np.nan

    price.price = price_val
    price.preference = pt
    return price


def read_price_book(path, session):

    stores = session.query(models.Store).filter(models.Store.active == True).all()
    store_dict = {store.name: store for store in stores}

    categories = session.query(models.Category).all()
    category_dict = {c.category: c for c in categories}

    pref_types = session.query(models.PreferenceType).all()
    pref_types = {pt.short: pt for pt in pref_types}
    # standard_pt = pref_types.get("S")

    df = pd.read_excel(path, na_filter=False)

    # trim all string values
    cols = ["category", "description", "pref_store"]
    df[cols] = df[cols].applymap(str.strip)

    # change all the store (price) columns into rows
    df = pd.melt(
        df,
        id_vars=["item_id", "category", "description", "pref_store"],
        var_name="store_name",
        value_name="price",
    )

    # add an Object column for the preferred store, category and Item
    df["pref_Store"] = df["pref_store"].apply(lambda x: store_dict.get(x))
    df["Category"] = df["category"].apply(lambda x: category_dict.get(x))
    df["Item"] = df["item_id"].apply(lambda id_: session.query(models.Item).get(id_))

    df["Item"] = df.apply(__update_item, axis=1)

    df["Store"] = df["store_name"].apply(lambda x: store_dict.get(x))

    df["Price"] = df.apply(
        lambda row: session.query(models.Price)
        .filter(
            models.Price.store_id == row["Store"].store_id,
            models.Price.item_id == row["item_id"],
        )
        .first(),
        axis=1,
    )

    df["Price"] = df.apply(__update_price, axis=1, preference_types=pref_types)

    session.flush()
