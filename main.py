from pathlib import Path

from groceries.db import models, populate, recreate_all, session

DATA_PATH = Path(".") / "data" / "setup"


def initial_populate():
    base = populate.get_base_items(DATA_PATH / "base items")

    base_items = []
    for _, items in base.items():
        base_items.extend(items)

    categories = [x for x in base_items if isinstance(x, models.Category)]
    units = [x for x in base_items if isinstance(x, models.Unit)]
    stores = [x for x in base_items if isinstance(x, models.Store)]
    preferences = [x for x in base_items if isinstance(x, models.PreferenceType)]

    items = populate.get_items(DATA_PATH / "items.csv", categories, units, stores)

    prices = populate.get_prices(DATA_PATH / "prices.csv", stores, items, preferences)

    session.add_all(base_items)
    session.add_all(items)
    session.add_all(prices)
    session.commit()


if __name__ == "__main__":
    recreate_all()
    initial_populate()
