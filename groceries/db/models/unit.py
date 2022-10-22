from sqlalchemy import Column, Integer, String

from .. import Base


class Unit(Base):
    __tablename__ = "Units"

    unit_id = Column("UnitID", Integer, primary_key=True, autoincrement=True)

    name = Column("Name", String, nullable=False, unique=True)
    symbol = Column("Symbol", String, nullable=True)

    def __init__(self, name, symbol=None):
        self.name = name
        self.symbol = symbol

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}', '{self.symbol}')"
