from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
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
    preference_type_id = Column(
        "PreferenceTypeID", Integer, ForeignKey("PreferenceTypes.TypeID"), nullable=True
    )

    price = Column("Price", Float, CheckConstraint('"Price" > 0'), nullable=True)

    store = relationship("Store")
    preference = relationship("PreferenceType")

    item = relationship("Item", back_populates="prices")

    __table_args__ = (UniqueConstraint("StoreID", "ItemID"),)

    def __init__(self, store, item, price, preference=None):
        self.store = store
        self.item = item
        self.price = price
        self.preference = preference

    def __repr__(self):
        return f"{self.store}, {self.item}, {self.price}, {self.preference}"
