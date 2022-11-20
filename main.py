from pathlib import Path

from groceries import create_price_book, generate_shopping_list, read_price_book
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


def run_generate_shopping_list():

    print("generate shopping list")
    generate_shopping_list(
        output_path=RESULTS_PATH / "shopping_list.xlsx",
        changed_path=RESULTS_PATH / "changed.xlsx",
        sql_path=SQL_PATH / "shopping_list.sql",
        session=session,
    )


def run_create_price_book():

    print("create price book")
    create_price_book(session, RESULTS_PATH / "price_book.xlsx")


def run_read_price_book():
    print("read price book")
    read_price_book(RESULTS_PATH / "price_book.xlsx", session)

    session.commit()


if __name__ == "__main__":
    # recreate_all()
    # initial_populate()

    # run_create_price_book()

    run_read_price_book()
    run_generate_shopping_list()
