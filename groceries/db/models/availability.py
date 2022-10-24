from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .. import Base


class Availability(Base):
    __tablename__ = "Availabilities"

    availability_id = Column(
        "AvailabilityID", Integer, primary_key=True, autoincrement=True
    )
    store_id = Column("StoreID", Integer, ForeignKey("Stores.StoreID"), nullable=False)
    item_id = Column("ItemID", Integer, ForeignKey("Items.ItemID"), nullable=False)

    availability = Column("Available", Boolean, nullable=False, default=False)

    note = Column("Notes", String)

    store = relationship("Store")
    item = relationship("Item")

    __table_args__ = (UniqueConstraint("StoreID", "ItemID"),)

    def __init__(self, store, item, availability=False, note=None):
        self.store = store
        self.item = item
        self.availability = availability
        self.note = note
