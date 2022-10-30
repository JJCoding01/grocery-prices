import pandas as pd

from .. import models


def __get_setup(path, func):

    df = pd.read_csv(path)
    df["model"] = df.apply(lambda row: func(row), axis=1)
    return df["model"].tolist()


def get_base_items(path):

    maps = {
        "categories.csv": lambda row: models.Category(
            category=row["category"], note=row["note"]
        ),
        "preference_types.csv": lambda row: models.PreferenceType(
            type_=row["type"], short=row["short"], note=row["note"]
        ),
        "stores.csv": lambda row: models.Store(
            name=row["name"], active=row["active"], cost=row["cost"]
        ),
        "units.csv": lambda row: models.Unit(row["unit"]),
    }

    data = {}
    for filename, func in maps.items():
        full_path = path / filename
        items = __get_setup(full_path, func)
        data.setdefault(filename, items)
        # print(items)
    return data


def get_items(items_path, categories_db, units_db):
    # must be done after base items have been loaded

    categories = {category.category: category for category in categories_db}
    units = {unit.unit: unit for unit in units_db}

    df = pd.read_csv(items_path)

    df.sort_values(by=["category", "name"], inplace=True)
    df["model"] = df.apply(
        lambda row: models.Item(
            name=row["name"],
            unit=units.get(row["unit"], None),
            category=categories.get(row["category"], None),
            note=row["note"],
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
            price_ = models.Price(
                store=store,
                item=item,
                price=price_val,
                date=None,
                check_price=False,
                note=None,
            )
            return price_
        if price_val in preferences:
            preference = models.Preference(
                store=store,
                item=item,
                preference=preferences.get(price_val, None),
                note=None,
            )
            return preference

        if price_val == "NA":
            availability = models.Availability(
                store=store, item=item, availability=False
            )
            return availability
        if price_val == "CHECK":
            price_ = models.Price(
                store=store,
                item=item,
                price=1000,
                date=None,
                check_price=True,
                note=None,
            )
            return price_

        return None

    stores = {store.name.lower(): store for store in stores_db}
    items = {item.name: item for item in items_db}
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
