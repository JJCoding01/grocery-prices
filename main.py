from pathlib import Path
import logging

from groceries import create_price_book, generate_shopping_list, read_price_book
from groceries.db import models, populate, recreate_all, session

DATA_PATH = Path(".") / "data" / "setup"
SQL_PATH = Path(".") / "sql"
RESULTS_PATH = Path(".") / "data" / "results"

logger = logging.getLogger("groceries")
logger.setLevel(logging.DEBUG)  # set logger level to the lowest used by any handler

sh = logging.StreamHandler()
fh = logging.FileHandler(Path(".") / "groceries.log", mode="w")
formatter = logging.Formatter(
    "%(asctime)-4s: %(levelname)-8s :: %(name)-32s :: %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)
fh.setFormatter(formatter)
sh.setFormatter(logging.Formatter("%(levelname)-8s :: %(name)-32s :: %(message)s"))

fh.setLevel(logging.DEBUG)
sh.setLevel(logging.INFO)

# add handlers to the logger
logger.addHandler(fh)
logger.addHandler(sh)

logger.debug(f"Database engine: {session.get_bind()}")


def run_generate_shopping_list():

    generate_shopping_list(
        output_path=RESULTS_PATH / "shopping_list.xlsx",
        changed_path=RESULTS_PATH / "changed.xlsx",
        sql_path=SQL_PATH / "shopping_list.sql",
        session=session,
    )


def run_create_price_book():
    create_price_book(session, RESULTS_PATH / "price_book.xlsx")


def run_read_price_book():
    read_price_book(RESULTS_PATH / "price_book.xlsx", session)

    session.commit()


def format_all():

    xl_sets = [("changed", "EFG"), ("shopping_list", "C"), ("price_book", "EFG")]
    for name, columns in xl_sets:
        path = RESULTS_PATH / f"{name}.xlsx"
        if not path.exists():
            continue

        wb = openpyxl.load_workbook(path, read_only=False)
        worksheet = wb.active
        format.column_width(worksheet)
        format.number_format(
            worksheet,
            column_letters=columns,
            format_=r"$* 0.000;[Color16]$* -0.000;-;[Color41]@",
        )

        wb.save(path)
        wb.close()


if __name__ == "__main__":
    # recreate_all()
    # populate.initial_populate(DATA_PATH, session)

    # run_create_price_book()

    run_read_price_book()
    run_generate_shopping_list()

    format_all()
