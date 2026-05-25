from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas.pokemon import (
    PokemonCreate,
    PokemonUpdate,
    PokemonResponse,
    PokemonListResponse,
)

router = APIRouter(prefix="/pokemons", tags=["Pokémons"])


@router.post(
    "/",
    response_model=PokemonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Pokémon",
    description="Registers a new Pokémon in the Pokédex. The name must be unique.",
)
def create_pokemon(pokemon_in: PokemonCreate, db: Session = Depends(get_db)):
    existing = crud.get_pokemon_by_name(db, pokemon_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Pokémon '{pokemon_in.name}' already exists.",
        )
    return crud.create_pokemon(db, pokemon_in)


@router.get(
    "/",
    response_model=PokemonListResponse,
    summary="List Pokémons",
    description=(
        "Returns a paginated list of Pokémons. "
        "Use `name` to search by name fragment and `type` to filter by type."
    ),
)
def list_pokemons(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    type: Optional[str] = Query(None, description="Filter by Pokémon type"),
    db: Session = Depends(get_db),
):
    total, results = crud.get_pokemons(
        db, skip=skip, limit=limit, type_filter=type, name_search=name
    )
    return PokemonListResponse(total=total, skip=skip, limit=limit, results=results)


@router.get(
    "/{pokemon_id}",
    response_model=PokemonResponse,
    summary="Get a Pokémon by ID",
)
def get_pokemon(pokemon_id: int, db: Session = Depends(get_db)):
    pokemon = crud.get_pokemon(db, pokemon_id)
    if not pokemon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pokémon with id {pokemon_id} not found.",
        )
    return pokemon


@router.get(
    "/name/{name}",
    response_model=PokemonResponse,
    summary="Get a Pokémon by name",
)
def get_pokemon_by_name(name: str, db: Session = Depends(get_db)):
    pokemon = crud.get_pokemon_by_name(db, name)
    if not pokemon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pokémon '{name}' not found.",
        )
    return pokemon


@router.patch(
    "/{pokemon_id}",
    response_model=PokemonResponse,
    summary="Partially update a Pokémon",
    description="Send only the fields you want to change.",
)
def update_pokemon(
    pokemon_id: int, pokemon_in: PokemonUpdate, db: Session = Depends(get_db)
):
    pokemon = crud.get_pokemon(db, pokemon_id)
    if not pokemon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pokémon with id {pokemon_id} not found.",
        )

    # Prevent duplicate name on update
    if pokemon_in.name:
        existing = crud.get_pokemon_by_name(db, pokemon_in.name)
        if existing and existing.id != pokemon_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Pokémon '{pokemon_in.name}' already exists.",
            )

    return crud.update_pokemon(db, pokemon, pokemon_in)


@router.delete(
    "/{pokemon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Pokémon",
)
def delete_pokemon(pokemon_id: int, db: Session = Depends(get_db)):
    pokemon = crud.get_pokemon(db, pokemon_id)
    if not pokemon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pokémon with id {pokemon_id} not found.",
        )
    crud.delete_pokemon(db, pokemon)
