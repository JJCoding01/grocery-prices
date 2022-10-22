from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .. import Base


class Category(Base):
    __tablename__ = "Categories"

    category_id = Column(
        "CategoryID", Integer, nullable=False, primary_key=True, autoincrement=True
    )

    category = Column("Category", String, nullable=False, unique=True)
    note = Column("Note", String, nullable=True)

    items = relationship("Item", back_populates="category")

    def __init__(self, category, note=None):
        self.category = category
        self.note = note

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.category}', '{self.note}')"
