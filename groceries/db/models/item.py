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

    description = Column("Description", String, nullable=False, unique=True)
    active = Column("Active", Boolean, nullable=False, default=True)

    unit = relationship("Unit")
    category = relationship("Category", back_populates="items")

    prices = relationship("Price", back_populates="item")

    def __init__(self, description, unit, category, note=None):
        self.description = description
        self.unit = unit
        self.category = category
        self.note = note

    def __repr__(self):
        return f"{self.__class__.__name__}({self.description}, {self.unit}, {self.category})"
