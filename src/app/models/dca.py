from sqlalchemy import Column, Integer, String
from .base import Base


class DCA(Base):
    __tablename__ = 'dca'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    midi_address = Column(String, nullable=False, unique=True)

