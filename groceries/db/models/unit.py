from sqlalchemy import Column, Integer, String

from .. import Base


class Unit(Base):
    __tablename__ = "Units"

    unit_id = Column("UnitID", Integer, primary_key=True, autoincrement=True)

    unit = Column("Unit", String, nullable=False, unique=True)

    def __init__(self, unit):
        self.unit = unit

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.unit}')"
