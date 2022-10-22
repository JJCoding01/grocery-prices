from datetime import datetime

from sqlalchemy import (
    Boolean, CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .. import Base


class Price(Base):
    __tablename__ = "Prices"

    price_id = Column("PriceID", Integer, primary_key=True, autoincrement=True)
    store_id = Column("StoreID", Integer, ForeignKey("Stores.StoreID"), nullable=False)
    item_id = Column("ItemID", Integer, ForeignKey("Items.ItemID"), nullable=False)

    price = Column("Price", Float, CheckConstraint('"Price" > 0'), nullable=False)
    date = Column("Date", DateTime, nullable=False, default=datetime.today)
    check_price = Column("Check", Boolean, nullable=False, default=False)
    note = Column("Notes", String)

    store = relationship("Store")
    # item = relationship("Item")

    item = relationship("Item", back_populates="prices")

    __table_args__ = (UniqueConstraint("StoreID", "ItemID"),)

    def __init__(self, store, item, price, date=None, check_price=False, note=None):
        self.store = store
        self.item = item
        self.price = price
        if date is None:
            self.date = datetime.today()
        else:
            self.date = date
        self.check_price = check_price
        self.note = note
