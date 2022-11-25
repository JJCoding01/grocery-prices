# pylint: disable=F
# flake8: noqa

import logging

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()

logger = logging.getLogger(__name__)

# must import models after Base is defined to avoid circular import error
from . import models  # isort:skip
from . import populate  # isort:skip

# path to project root
PATH = Path(__file__).parent.parent.parent.absolute()

DATABASE_URI = f"sqlite:///{PATH / 'test_groceries.db'}"


engine = create_engine(DATABASE_URI)
session = Session(bind=engine)


def recreate_all():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine, checkfirst=False)
    logger.info("recreated database")
