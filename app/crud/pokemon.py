from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.pokemon import Pokemon
from app.schemas.pokemon import PokemonCreate, PokemonUpdate


def get_pokemon(db: Session, pokemon_id: int) -> Optional[Pokemon]:
    """Fetch a single Pokémon by its primary key."""
    return db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()


def get_pokemon_by_name(db: Session, name: str) -> Optional[Pokemon]:
    """Fetch a single Pokémon by name (case-insensitive)."""
    return (
        db.query(Pokemon)
        .filter(Pokemon.name.ilike(name))
        .first()
    )


def get_pokemons(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    type_filter: Optional[str] = None,
    name_search: Optional[str] = None,
) -> tuple[int, List[Pokemon]]:
    """
    Return (total_count, page_of_pokemons).
    Supports optional filtering by type and name search.
    """
    query = db.query(Pokemon)

    if name_search:
        query = query.filter(Pokemon.name.ilike(f"%{name_search}%"))

    if type_filter:
        # JSON 'contains' check — works for SQLite and PostgreSQL
        query = query.filter(Pokemon.types.contains([type_filter.lower()]))

    total = query.count()
    results = query.offset(skip).limit(limit).all()
    return total, results


def create_pokemon(db: Session, pokemon_in: PokemonCreate) -> Pokemon:
    """Insert a new Pokémon record."""
    db_pokemon = Pokemon(
        name=pokemon_in.name.lower(),
        types=[t.lower() for t in pokemon_in.types],
        abilities=[a.lower() for a in pokemon_in.abilities],
        hp=pokemon_in.hp,
        attack=pokemon_in.attack,
        defense=pokemon_in.defense,
        speed=pokemon_in.speed,
        height=pokemon_in.height,
        weight=pokemon_in.weight,
        sprite_url=pokemon_in.sprite_url,
    )
    db.add(db_pokemon)
    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon


def update_pokemon(
    db: Session, db_pokemon: Pokemon, pokemon_in: PokemonUpdate
) -> Pokemon:
    """Apply a partial update to an existing Pokémon."""
    update_data = pokemon_in.model_dump(exclude_unset=True)

    # Normalise strings to lowercase when provided
    if "name" in update_data:
        update_data["name"] = update_data["name"].lower()
    if "types" in update_data:
        update_data["types"] = [t.lower() for t in update_data["types"]]
    if "abilities" in update_data:
        update_data["abilities"] = [a.lower() for a in update_data["abilities"]]

    for field, value in update_data.items():
        setattr(db_pokemon, field, value)

    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon


def delete_pokemon(db: Session, db_pokemon: Pokemon) -> None:
    """Delete a Pokémon record from the database."""
    db.delete(db_pokemon)
    db.commit()
