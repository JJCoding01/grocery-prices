import logging

import numpy as np
import pandas as pd

from .. import models

logger = logging.getLogger(__name__)


def __get_setup(path, func):

    df = pd.read_csv(path, na_filter=False)
    df["model"] = df.apply(lambda row: func(row), axis=1)
    return df["model"].tolist()


def get_base_items(path):

    maps = {
        "categories.csv": lambda row: models.Category(category=row["category"]),
        "preference_types.csv": lambda row: models.PreferenceType(
            type_=row["type"], short=row["short"]
        ),
        "stores.csv": lambda row: models.Store(name=row["name"], active=row["active"]),
        "units.csv": lambda row: models.Unit(row["unit"]),
    }

    data = {}
    for filename, func in maps.items():
        full_path = path / filename
        items = __get_setup(full_path, func)
        data.setdefault(filename, items)
        # print(items)
    return data


def get_items(items_path, categories_db, units_db, stores_db):
    # must be done after base items have been loaded

    categories = {category.category: category for category in categories_db}
    units = {unit.unit: unit for unit in units_db}
    stores = {store.name: store for store in stores_db}

    df = pd.read_csv(items_path)

    df["model"] = df.apply(
        lambda row: models.Item(
            description=row["description"],
            unit=units.get(row["unit"], None),
            category=categories.get(row["category"], None),
            preferred_store=stores.get(row["preferred_store"]),
        ),
        axis=1,
    )
    items = df["model"].tolist()

    return items


def __create_price(row):
    store = row["Store"]
    item = row["Item"]
    price_val = row["price"]
    pref = row["Preference"]

    if np.isnan(price_val) and pref.short == "S":
        return None
    price_ = models.Price(store=store, item=item, price=price_val, preference=pref)
    return price_


def __parse_price(price_):
    try:
        return float(price_)
    except ValueError:
        return np.nan


def get_prices(price_path, stores_db, items_db, preferences_db):
    stores = {store.name.lower(): store for store in stores_db}
    items = {item.description: item for item in items_db}
    preferences = {preference.short: preference for preference in preferences_db}

    df = pd.read_csv(price_path)

    # change all the store (price) columns into rows
    df = pd.melt(
        df, id_vars=["index", "item"], var_name="store_name", value_name="price_raw"
    )

    df["Store"] = df["store_name"].apply(lambda x: stores.get(x))
    df["Item"] = df["item"].apply(lambda x: items.get(x))
    df["price_raw"] = (
        df["price_raw"]
        .apply(lambda x: str(x).replace("$", ""))
        .apply(lambda x: x.strip())
        .astype(float, errors="ignore")
    )
    df["Preference"] = df["price_raw"].apply(
        lambda x: preferences.get(x, preferences["S"])
    )
    df["price"] = df["price_raw"].apply(__parse_price)

    df["Price"] = df.apply(__create_price, axis=1)
    df["preference_type"] = df["Preference"].apply(
        lambda x: None if x is None else x.short
    )

    # remove rows that have both a standard preference type and no price.
    # Those are simply blank, storing these in the price table has no value.
    # Do this by selecting all rows where the price is not nan or the preference is not
    # standard
    df = df[(~np.isnan(df["price"])) | (df["preference_type"] != "S")]

    df = df.sort_values(by="preference_type")
    prices = df["Price"].tolist()

    return prices


def initial_populate(data_path, session):

    base = get_base_items(data_path / "base items")

    base_items = []
    for _, items in base.items():
        base_items.extend(items)

    categories = [x for x in base_items if isinstance(x, models.Category)]
    units = [x for x in base_items if isinstance(x, models.Unit)]
    stores = [x for x in base_items if isinstance(x, models.Store)]
    preferences = [x for x in base_items if isinstance(x, models.PreferenceType)]

    items = get_items(data_path / "items.csv", categories, units, stores)

    prices = get_prices(data_path / "prices.csv", stores, items, preferences)

    session.add_all(base_items)
    session.add_all(items)
    session.add_all(prices)
    session.commit()

    logger.info(f"repopulated database with sample data and commit")
