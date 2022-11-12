import numpy as np
import pandas as pd

from groceries.db import models


def __create_item_description(row, description_col="item", unit_col="unit"):
    """
    Create item description by combining item description and item unit

    This is a private function and is used internally to generate user-facing
    descriptions, that include the units, where applicable.

    Parameters
    ----------
    row : Dataframe row
        The row is expected to have an `item` column, and a `unit` column
    description_col : str, optional
        name of the DataFrame column where the item description is found. Defaults to
        `description_col="item"`
    unit_col : str, optional
        name of the DataFrame column where the unit is found

    Returns
    -------
    str : combination of item description and unit. Returns just description when
        unit is `None`
    """
    description_ = row[description_col]
    unit_ = row[unit_col]

    if unit_ is None:
        return description_
    return f"{description_} (per {unit_})"


def __price(row, pref_col="pt", price_col="price", standard_pt="S"):
    """
    Read proper price from DataFrame

    Parameters
    ----------
    row : DataFrame row
        This is expected to have a preference type column and a price column
    pref_col : str, optional
        name of preference type column, defaults to 'pt'
    price_col : str, optional
        name or price column, defaults to 'price'
    standard_pt : str, optional
        standard preference type string (default is "S"). Any preference types of this
        category are simply returned

    Returns
    -------
    numeric or str
        price as a decimal when pref_col is equal to None or price_col = standard_pt
    """
    pt_ = row[pref_col]  # preference type (short)
    price_ = row[price_col]

    if pt_ is None or pt_ == standard_pt:
        return price_
    return pt_


def create_price_book(session, out_path):

    # read all item and price data from database and add them to a dataframe
    results = session.query(models.Item, models.Price).outerjoin(models.Price).all()

    # convert results into dataframe with Item and Price (upper case) column names
    df = pd.DataFrame(results, columns=["Item", "Price"])

    # now, process the Item and Price objects and add columns for all rows
    df["item_id"] = df["Item"].apply(lambda x: x.item_id)
    df["item"] = df["Item"].apply(lambda x: x.description)
    df["category"] = df["Item"].apply(
        lambda x: None if x.category is None else x.category.category
    )
    df["unit"] = df["Item"].apply(lambda x: None if x.unit is None else x.unit.unit)
    df["store"] = df["Price"].apply(lambda x: None if x is None else x.store.name)
    df["pt"] = df["Price"].apply(
        lambda x: np.nan if x is None or x.preference is None else x.preference.short
    )
    df["price"] = df["Price"].apply(lambda x: None if x is None else x.price)

    df["price"] = df[["pt", "price"]].apply(lambda row: __price(row), axis=1)
    df["description"] = df[["item", "unit"]].apply(
        lambda row: __create_item_description(row), axis=1
    )

    # create dataframe of distinct items and ids
    price_book = df[["item_id", "category", "description"]].drop_duplicates(
        subset=["item_id"]
    )

    # create a list of all stores that are in the query (had prices)
    # note that this does not affect the standard df (inplace=False)
    stores = df["store"].dropna().unique()

    # iterate over stores and merge prices into price book based on item ID
    for store in stores:
        # get dataframe of item ID and price for each item for current store
        price_df = df[["item_id", "store", "price"]]
        price_df = price_df[price_df["store"] == store]  # select only current store
        price_df = price_df[
            ["item_id", "price"]
        ]  # only item ID and price columns needed

        # merge the price for the current store with the item description dataframe, and
        # rename price column to match store name
        price_book = pd.merge(price_book, price_df, on="item_id", validate="1:1")
        price_book = price_book.rename(columns={"price": store})

    price_book = price_book.sort_values(by=["category", "description"])

    if out_path is not None:
        price_book.to_excel(out_path, index=False)
    return price_book
