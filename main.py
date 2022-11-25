from pathlib import Path

from groceries import create_price_book, generate_shopping_list, read_price_book
from groceries.db import models, populate, recreate_all, session

DATA_PATH = Path(".") / "data" / "setup"
SQL_PATH = Path(".") / "sql"
RESULTS_PATH = Path(".") / "data" / "results"


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
    # populate.initial_populate(DATA_PATH, session)

    # run_create_price_book()

    run_read_price_book()
    run_generate_shopping_list()
