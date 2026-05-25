from sqlalchemy import Column, Integer, String, Float, ARRAY
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy import JSON

from app.database import Base


class Pokemon(Base):
    __tablename__ = "pokemons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    types = Column(JSON, nullable=False, default=list)       # e.g. ["fire", "flying"]
    abilities = Column(JSON, nullable=False, default=list)   # e.g. ["blaze", "solar-power"]
    hp = Column(Integer, nullable=False, default=0)
    attack = Column(Integer, nullable=False, default=0)
    defense = Column(Integer, nullable=False, default=0)
    speed = Column(Integer, nullable=False, default=0)
    height = Column(Float, nullable=False, default=0.0)      # in meters
    weight = Column(Float, nullable=False, default=0.0)      # in kg
    sprite_url = Column(String(255), nullable=True)
