from datetime import datetime
from pathlib import Path

import numpy as np

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from groceries.db import Base, models

PATH = Path(__file__).parent.absolute()

DATABASE_URI = f"sqlite:///{PATH / 'test_groceries.db'}"
print(DATABASE_URI)

engine = create_engine(DATABASE_URI)
session = Session(bind=engine)


def populate_stores():
    names = ["Wal-Mart", "Costco", "Aldi"]

    for name in names:
        store = models.Store(name)
        session.add(store)

    session.commit()


def populate_categories():
    categories = ["Frozen", "dairy", "meat", "misc"]
    for name in categories:
        category = models.Category(category=name)
        session.add(category)
    session.commit()


def populate_preference_types():
    types = [
        ("Preferred", "P"),
        ("Not Preferred", "NP"),
    ]
    for name, short in types:
        preference_type = models.PreferenceType(type_=name, short=short)
        session.add(preference_type)
    session.commit()


def populate_items():
    units = session.query(models.Unit).all()
    categories = session.query(models.Category).all()

    for category in categories:
        for unit in units:
            for k in range(3):
                item = models.Item(
                    f"{category.category}: {k} item per {unit.symbol}",
                    unit=unit,
                    category=category,
                )
                session.add(item)
    session.commit()


def populate_prices():
    items = session.query(models.Item).all()
    stores = session.query(models.Store).all()

    for store in stores:
        for item in items:
            price = models.Price(
                store,
                item,
                np.random.randint(1, 15),
                date=datetime.today(),
                note="for today",
            )
            session.add(price)

    session.commit()


def populate_units():
    units = [
        ("Gallon", "gal"),
        ("Ounce", "oz"),
        ("Fluid-Ounce", "fl-oz"),
        ("Pound", "lb"),
        ("Each", "ea"),
        ("Package", "pk"),
        ("Box", "bx"),
    ]
    for name, symbol in units:
        unit = models.Unit(name=name, symbol=symbol)
        session.add(unit)
    session.commit()


def populate_preferences():
    items = session.query(models.Item).all()
    stores = session.query(models.Store).all()
    preference_types = session.query(models.PreferenceType).all()

    for store in stores:
        for item in np.random.choice(items, np.random.randint(1, 10, 1), replace=False):
            preference_type = np.random.choice(preference_types, 1)[0]
            preference = models.Preference(store, item, preference_type)
            session.add(preference)
    session.commit()


def add_data():
    populate_stores()
    populate_categories()
    populate_units()
    populate_preference_types()
    populate_items()
    populate_prices()
    populate_preferences()


def recreate_all():
    # print('start recreating tables...')
    # print(Base.metadata.tables.keys())
    Base.metadata.drop_all(engine)
    # print('tables dropped...')
    Base.metadata.create_all(engine, checkfirst=False)
    # print('finished recreating...')


def query():
    category = session.query(models.Category).first()

    print(category)

    items = category.items
    item = items[0]
    prices = item.prices

    print(item)
    print(prices)
    for price in prices:
        print(price.price)
    # for item in items:
    #     print(item)


if __name__ == "__main__":
    recreate_all()
    add_data()
    query()
