from sqlalchemy import Boolean, Column, Integer, String

from .. import Base


class Store(Base):
    __tablename__ = "Stores"

    store_id = Column(
        "StoreID", Integer, nullable=False, primary_key=True, autoincrement=True
    )

    name = Column("Store", String, nullable=False, unique=True)
    active = Column("Active", Boolean, nullable=False, default=True)

    def __init__(self, name, active=True):
        self.name = name
        self.active = active

    def __repr__(self):
        return f"{self.__name__}('{self.name}')"
