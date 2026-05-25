from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class PokemonBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["charizard"])
    types: List[str] = Field(..., min_length=1, examples=[["fire", "flying"]])
    abilities: List[str] = Field(..., min_length=1, examples=[["blaze", "solar-power"]])
    hp: int = Field(..., ge=1, le=999, examples=[78])
    attack: int = Field(..., ge=1, le=999, examples=[84])
    defense: int = Field(..., ge=1, le=999, examples=[78])
    speed: int = Field(..., ge=1, le=999, examples=[100])
    height: float = Field(..., gt=0, examples=[1.7])
    weight: float = Field(..., gt=0, examples=[90.5])
    sprite_url: Optional[str] = Field(None, examples=["https://example.com/charizard.png"])


class PokemonCreate(PokemonBase):
    """Schema for creating a new Pokémon."""
    pass


class PokemonUpdate(BaseModel):
    """Schema for partially updating a Pokémon (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    types: Optional[List[str]] = Field(None, min_length=1)
    abilities: Optional[List[str]] = Field(None, min_length=1)
    hp: Optional[int] = Field(None, ge=1, le=999)
    attack: Optional[int] = Field(None, ge=1, le=999)
    defense: Optional[int] = Field(None, ge=1, le=999)
    speed: Optional[int] = Field(None, ge=1, le=999)
    height: Optional[float] = Field(None, gt=0)
    weight: Optional[float] = Field(None, gt=0)
    sprite_url: Optional[str] = None


class PokemonResponse(PokemonBase):
    """Schema for returning a Pokémon from the API."""
    id: int

    model_config = {"from_attributes": True}


class PokemonListResponse(BaseModel):
    """Paginated list of Pokémon."""
    total: int
    skip: int
    limit: int
    results: List[PokemonResponse]
