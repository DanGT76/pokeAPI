"""
Unit tests for the Pokémon API endpoints.
Covers: create, list, get by id/name, update, delete and edge cases.
"""
import pytest


# ---------------------------------------------------------------------------
# POST /api/v1/pokemons/
# ---------------------------------------------------------------------------

class TestCreatePokemon:
    def test_create_pokemon_success(self, client, sample_pokemon_payload):
        response = client.post("/api/v1/pokemons/", json=sample_pokemon_payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "pikachu"
        assert data["types"] == ["electric"]
        assert data["hp"] == 35
        assert "id" in data

    def test_create_pokemon_duplicate_name(self, client, created_pokemon, sample_pokemon_payload):
        response = client.post("/api/v1/pokemons/", json=sample_pokemon_payload)

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_create_pokemon_name_is_lowercased(self, client, sample_pokemon_payload):
        sample_pokemon_payload["name"] = "CHARIZARD"
        response = client.post("/api/v1/pokemons/", json=sample_pokemon_payload)

        assert response.status_code == 201
        assert response.json()["name"] == "charizard"

    def test_create_pokemon_missing_required_field(self, client, sample_pokemon_payload):
        del sample_pokemon_payload["name"]
        response = client.post("/api/v1/pokemons/", json=sample_pokemon_payload)

        assert response.status_code == 422  # Unprocessable Entity

    def test_create_pokemon_invalid_hp(self, client, sample_pokemon_payload):
        sample_pokemon_payload["hp"] = 0  # must be >= 1
        response = client.post("/api/v1/pokemons/", json=sample_pokemon_payload)

        assert response.status_code == 422

    def test_create_pokemon_empty_types(self, client, sample_pokemon_payload):
        sample_pokemon_payload["types"] = []
        response = client.post("/api/v1/pokemons/", json=sample_pokemon_payload)

        assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/pokemons/
# ---------------------------------------------------------------------------

class TestListPokemons:
    def test_list_empty(self, client):
        response = client.get("/api/v1/pokemons/")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["results"] == []

    def test_list_with_one_pokemon(self, client, created_pokemon):
        response = client.get("/api/v1/pokemons/")

        data = response.json()
        assert data["total"] == 1
        assert len(data["results"]) == 1

    def test_list_pagination(self, client, client_with_multiple_pokemons):
        response = client.get("/api/v1/pokemons/?skip=0&limit=2")
        data = response.json()

        assert len(data["results"]) == 2
        assert data["skip"] == 0
        assert data["limit"] == 2

    def test_list_filter_by_type(self, client, client_with_multiple_pokemons):
        response = client.get("/api/v1/pokemons/?type=electric")
        data = response.json()

        assert data["total"] >= 1
        for pokemon in data["results"]:
            assert "electric" in pokemon["types"]

    def test_list_search_by_name(self, client, created_pokemon):
        response = client.get("/api/v1/pokemons/?name=pika")
        data = response.json()

        assert data["total"] == 1
        assert data["results"][0]["name"] == "pikachu"

    def test_list_search_no_match(self, client, created_pokemon):
        response = client.get("/api/v1/pokemons/?name=mewtwo")
        data = response.json()

        assert data["total"] == 0


# ---------------------------------------------------------------------------
# GET /api/v1/pokemons/{id}
# ---------------------------------------------------------------------------

class TestGetPokemonById:
    def test_get_existing_pokemon(self, client, created_pokemon):
        pokemon_id = created_pokemon["id"]
        response = client.get(f"/api/v1/pokemons/{pokemon_id}")

        assert response.status_code == 200
        assert response.json()["id"] == pokemon_id

    def test_get_nonexistent_pokemon(self, client):
        response = client.get("/api/v1/pokemons/9999")

        assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/v1/pokemons/name/{name}
# ---------------------------------------------------------------------------

class TestGetPokemonByName:
    def test_get_by_name_success(self, client, created_pokemon):
        response = client.get("/api/v1/pokemons/name/pikachu")

        assert response.status_code == 200
        assert response.json()["name"] == "pikachu"

    def test_get_by_name_case_insensitive(self, client, created_pokemon):
        response = client.get("/api/v1/pokemons/name/PIKACHU")

        assert response.status_code == 200

    def test_get_by_name_not_found(self, client):
        response = client.get("/api/v1/pokemons/name/unknownmon")

        assert response.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /api/v1/pokemons/{id}
# ---------------------------------------------------------------------------

class TestUpdatePokemon:
    def test_update_single_field(self, client, created_pokemon):
        pokemon_id = created_pokemon["id"]
        response = client.patch(
            f"/api/v1/pokemons/{pokemon_id}", json={"hp": 999}
        )

        assert response.status_code == 200
        assert response.json()["hp"] == 999
        # Other fields must remain unchanged
        assert response.json()["name"] == "pikachu"

    def test_update_multiple_fields(self, client, created_pokemon):
        pokemon_id = created_pokemon["id"]
        response = client.patch(
            f"/api/v1/pokemons/{pokemon_id}",
            json={"attack": 120, "speed": 110},
        )

        data = response.json()
        assert data["attack"] == 120
        assert data["speed"] == 110

    def test_update_nonexistent_pokemon(self, client):
        response = client.patch("/api/v1/pokemons/9999", json={"hp": 100})

        assert response.status_code == 404

    def test_update_duplicate_name(self, client_with_multiple_pokemons):
        # Try renaming pikachu to bulbasaur (which already exists)
        pikachu = client_with_multiple_pokemons.get("/api/v1/pokemons/name/pikachu").json()
        response = client_with_multiple_pokemons.patch(
            f"/api/v1/pokemons/{pikachu['id']}", json={"name": "bulbasaur"}
        )

        assert response.status_code == 409

    def test_update_invalid_value(self, client, created_pokemon):
        pokemon_id = created_pokemon["id"]
        response = client.patch(
            f"/api/v1/pokemons/{pokemon_id}", json={"hp": 0}
        )

        assert response.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /api/v1/pokemons/{id}
# ---------------------------------------------------------------------------

class TestDeletePokemon:
    def test_delete_existing_pokemon(self, client, created_pokemon):
        pokemon_id = created_pokemon["id"]
        response = client.delete(f"/api/v1/pokemons/{pokemon_id}")

        assert response.status_code == 204

    def test_deleted_pokemon_is_gone(self, client, created_pokemon):
        pokemon_id = created_pokemon["id"]
        client.delete(f"/api/v1/pokemons/{pokemon_id}")

        response = client.get(f"/api/v1/pokemons/{pokemon_id}")
        assert response.status_code == 404

    def test_delete_nonexistent_pokemon(self, client):
        response = client.delete("/api/v1/pokemons/9999")

        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

class TestHealthCheck:
    def test_health_check(self, client):
        response = client.get("/")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# Helpers / additional fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client_with_multiple_pokemons(client):
    """Seed three Pokémons (including one electric) for tests that need multiple records."""
    pokemons = [
        {
            "name": "pikachu",
            "types": ["electric"],
            "abilities": ["static", "lightning-rod"],
            "hp": 35, "attack": 55, "defense": 40, "speed": 90,
            "height": 0.4, "weight": 6.0,
        },
        {
            "name": "bulbasaur",
            "types": ["grass", "poison"],
            "abilities": ["overgrow"],
            "hp": 45, "attack": 49, "defense": 49, "speed": 45,
            "height": 0.7, "weight": 6.9,
        },
        {
            "name": "squirtle",
            "types": ["water"],
            "abilities": ["torrent"],
            "hp": 44, "attack": 48, "defense": 65, "speed": 43,
            "height": 0.5, "weight": 9.0,
        },
    ]
    for p in pokemons:
        client.post("/api/v1/pokemons/", json=p)
    return client
