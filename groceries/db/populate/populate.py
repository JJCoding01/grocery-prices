import pandas as pd

from .. import models


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


def get_prices(price_path, stores_db, items_db, preferences_db):
    def create_price(row, store_name):
        store = stores.get(store_name, None)
        item = items.get(row["item"])
        price_val = row[store_name]
        try:
            price_val = float(price_val)
        except ValueError:
            pass
        if isinstance(price_val, float):
            pref = preferences.get("S")
            price_ = models.Price(
                store=store,
                item=item,
                price=price_val,
                preference=pref,
            )
            return price_
        if price_val in preferences:
            pref = preferences.get(price_val)
            price_ = models.Price(
                store=store,
                item=item,
                price=None,
                preference=pref,
            )
            return price_

        return None

    stores = {store.name.lower(): store for store in stores_db}
    items = {item.description: item for item in items_db}
    preferences = {preference.short: preference for preference in preferences_db}

    df = pd.read_csv(price_path)

    # convert all prices to numerical values. Keeping various notes that are not numbers
    store_names = [store.lower() for store in stores]
    prices = []
    for store in store_names:
        df[store] = (
            df[store].apply(lambda x: x.replace("$", "")).apply(lambda x: x.strip())
        )
        df[store] = df[store].astype(float, errors="ignore")

        df[f"{store}_model"] = df.apply(lambda row: create_price(row, store), axis=1)
        store_prices = df[f"{store}_model"].tolist()
        store_prices = [p for p in store_prices if p is not None]
        prices.extend(store_prices)
    return prices
