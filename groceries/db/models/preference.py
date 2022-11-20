from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .. import Base


class Preference(Base):
    __tablename__ = "Preferences"

    preference_id = Column("PriceID", Integer, primary_key=True, autoincrement=True)
    store_id = Column("StoreID", Integer, ForeignKey("Stores.StoreID"), nullable=False)
    item_id = Column("ItemID", Integer, ForeignKey("Items.ItemID"), nullable=False)
    preference_type_id = Column(
        "PreferenceTypeID",
        Integer,
        ForeignKey("PreferenceTypes.TypeID"),
        nullable=False,
    )

    note = Column("Notes", String)

    store = relationship("Store")
    item = relationship("Item")
    preference = relationship("PreferenceType")

    __table_args__ = (UniqueConstraint("StoreID", "ItemID"),)

    def __init__(self, store, item, preference, note=None):
        self.store = store
        self.item = item
        self.preference = preference
        self.note = note


class PreferenceType(Base):
    __tablename__ = "PreferenceTypes"

    type_id = Column("TypeID", Integer, primary_key=True, autoincrement=True)
    type_ = Column("Type", String, nullable=False, unique=True)
    short = Column("ShortType", String, nullable=True)

    def __init__(self, type_, short=None):
        self.type_ = type_
        self.short = short

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.type_}', '{self.short}')"
