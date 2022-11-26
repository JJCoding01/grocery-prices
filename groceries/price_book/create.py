import logging

import numpy as np
import pandas as pd

from groceries.db import models

logger = logging.getLogger(__name__)


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


def __preferred_store(x):
    if x is None:
        return None
    store = x.preferred_store
    if store is None:
        return None
    return store.name


def __store_names(session, active=True):
    """return list of active store names"""
    stores = session.query(models.Store).filter(models.Store.active == active).all()
    store_names = [s.name for s in stores]
    store_names.sort()
    return store_names


def __parse_pref_type(x):
    if x is None or x.preference is None:
        return np.nan
    return x.preference.short


def __parse_category(x):
    if x.category is None:
        return
    return x.category.category


def create_price_book(session, out_path):

    logger.debug(f"start generating price book at: {out_path}")

    # Items that DO have a Price, and add the Item and Price objects to a DataFrame
    result_query = session.query(models.Item, models.Price).outerjoin(models.Price)
    results = result_query.all()
    df = pd.DataFrame(results, columns=["Item", "Price"])

    # get items that do NOT have a price
    sub_query = session.query(models.Price.item_id)
    results = session.query(models.Item).where(models.Item.item_id.not_in(sub_query))
    results = results.all()
    df_no_prices = pd.DataFrame(results, columns=["Item"])

    # now, process the Price object by extracting key Price related columns. Note that
    # everything in the dataframe is guaranteed to have a Price object, because of the
    # query; it was pulling from the Price table in the DB
    df["store"] = df["Price"].apply(lambda x: None if x is None else x.store.name)
    df["pt"] = df["Price"].apply(__parse_pref_type)
    df["price"] = df["Price"].apply(lambda x: None if x is None else x.price)
    df["price"] = df[["pt", "price"]].apply(__price, axis=1)

    # Now that all price related columns have been processed, combine the Items that do
    # not have a price. From here down, the Price object does not exist for all rows,
    # but the Item object does exist for all rows.
    df = pd.concat([df, df_no_prices], ignore_index=True)

    df["item_id"] = df["Item"].apply(lambda x: x.item_id)
    df["item"] = df["Item"].apply(lambda x: x.description)
    df["category"] = df["Item"].apply(__parse_category)
    df["unit"] = df["Item"].apply(lambda x: None if x.unit is None else x.unit.unit)
    df["pref_store"] = df["Item"].apply(__preferred_store)
    df["description"] = df[["item", "unit"]].apply(__create_item_description, axis=1)

    # create dataframe of distinct items, this will serve as the price book DataFrame.
    # The store price columns will be merged into this DataFrame
    price_book = df[
        ["item_id", "category", "description", "pref_store"]
    ].drop_duplicates(subset=["item_id"])

    # create a list of all stores that are in the query (had prices)
    # note that this does not affect the standard df (inplace=False)
    stores = __store_names(session, active=True)

    # iterate over stores and merge prices into price book based on item ID
    for store in stores:
        logger.debug(f"process prices for price book for '{store}'")
        # get dataframe of item ID and price for each item for current store
        price_df = df[["item_id", "store", "price"]]
        price_df = price_df[price_df["store"] == store]  # select only current store

        # only item ID and price columns needed
        price_df = price_df[["item_id", "price"]]

        # merge the price for the current store with the item description dataframe, and
        # rename price column to match store name
        price_book = pd.merge(
            price_book, price_df, on="item_id", how="outer", validate="1:1"
        )
        price_book = price_book.rename(columns={"price": store})

    price_book = price_book.sort_values(by=["category", "description"])

    if out_path is not None:
        logger.debug(f"export price book: {out_path}")
        price_book.to_excel(out_path, index=False)
    return price_book
