from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .. import Base


class Item(Base):
    __tablename__ = "Items"

    item_id = Column("ItemID", Integer, primary_key=True, autoincrement=True)
    unit_id = Column("UnitID", Integer, ForeignKey("Units.UnitID"), nullable=True)
    category_id = Column(
        "CategoryID", Integer, ForeignKey("Categories.CategoryID"), nullable=True
    )
    preferred_store_id = Column(
        "PreferredStoreID", Integer, ForeignKey("Stores.StoreID"), nullable=True
    )

    description = Column("Description", String, nullable=False, unique=True)
    active = Column("Active", Boolean, nullable=False, default=True)

    unit = relationship("Unit")
    preferred_store = relationship("Store")
    category = relationship("Category", back_populates="items")

    prices = relationship("Price", back_populates="item")

    def __init__(self, description, unit, category, preferred_store=None):
        self.description = description
        self.unit = unit
        self.category = category
        self.preferred_store = preferred_store

    def __repr__(self):
        return f"{self.__class__.__name__}({self.description}, {self.unit}, {self.category})"
