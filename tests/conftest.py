import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Use an isolated in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test function."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """TestClient with the test database injected."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_pokemon_payload():
    return {
        "name": "pikachu",
        "types": ["electric"],
        "abilities": ["static", "lightning-rod"],
        "hp": 35,
        "attack": 55,
        "defense": 40,
        "speed": 90,
        "height": 0.4,
        "weight": 6.0,
        "sprite_url": "https://example.com/pikachu.png",
    }


@pytest.fixture
def created_pokemon(client, sample_pokemon_payload):
    """Creates a Pokémon in the DB and returns the response JSON."""
    response = client.post("/api/v1/pokemons/", json=sample_pokemon_payload)
    assert response.status_code == 201
    return response.json()
