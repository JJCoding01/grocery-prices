from pathlib import Path

import pandas as pd
from sqlalchemy import text

from groceries.db import models, populate, recreate_all, session

DATA_PATH = Path(".") / "data" / "setup"
SQL_PATH = Path(".") / "sql"
RESULTS_PATH = Path(".") / "data" / "results"


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


def create_shopping_list():
    filename = SQL_PATH / "shopping_list.sql"
    results_filename = RESULTS_PATH / "shopping_list.xlsx"

    # columns defined by sql query
    columns = ["store", "category", "item", "price"]

    stores = session.query(models.Store).filter(models.Store.active == 1).all()
    store_names = [store.name for store in stores]
    with open(filename, "r") as f:
        sql = text(f.read())

    engine = session.get_bind()
    results = engine.execute(sql)
    table = {column: [] for column in columns}
    for result in results:
        for column, value in zip(columns, result):
            table[column].append(value)

    df = pd.DataFrame(table)
    df = df.sort_values(by=columns)
    with pd.ExcelWriter(results_filename) as writer:
        for store_name in store_names:
            df[df["store"] == store_name][columns[1:]].to_excel(
                writer, sheet_name=store_name, index=False
            )


if __name__ == "__main__":
    recreate_all()
    initial_populate()
    create_shopping_list()
