import numpy as np

from sqlalchemy import Boolean, Column, Float, Integer, String

from .. import Base


class Store(Base):
    __tablename__ = "Stores"

    store_id = Column(
        "StoreID", Integer, nullable=False, primary_key=True, autoincrement=True
    )

    name = Column("Store", String, nullable=False, unique=True)
    membership = Column("RequiresMembership", Boolean, nullable=False, default=False)
    membership_cost = Column("MembershipCost", Float, nullable=True)
    active = Column("Active", Boolean, nullable=False, default=True)

    def __init__(self, name, cost=None, active=True):
        self.name = name
        self.membership_cost = cost
        self.active = active
        self.membership = not np.isnan(cost)

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"
