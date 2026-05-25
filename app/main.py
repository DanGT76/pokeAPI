from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import pokemon_router

# Create all tables on startup (use Alembic migrations in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PokéAPI Clone",
    description=(
        "Uma API RESTful inspirada na PokéAPI, construída com **FastAPI** e **SQLAlchemy**.\n\n"
        "## Funcionalidades\n"
        "- 🔍 Buscar Pokémons por ID ou nome\n"
        "- 📋 Listar com paginação e filtros por tipo\n"
        "- ➕ Criar novos Pokémons\n"
        "- ✏️ Atualizar parcialmente\n"
        "- 🗑️ Deletar\n"
    ),
    version="1.0.0",
    contact={
        "name": "Pokédex API",
        "url": "https://github.com/seu-usuario/pokemon-api",
    },
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pokemon_router, prefix="/api/v1")


@app.get("/", tags=["Health"], summary="Health check")
def health_check():
    """Returns API status."""
    return {"status": "ok", "message": "Pokédex API is running! 🚀"}
