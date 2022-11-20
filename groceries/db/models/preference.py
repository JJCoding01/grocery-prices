from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .. import Base


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
