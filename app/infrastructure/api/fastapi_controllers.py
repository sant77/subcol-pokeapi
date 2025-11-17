from fastapi import APIRouter
from pydantic import BaseModel
from application.use_cases import BestCounterUseCase
from infrastructure.pokeapi.pokemon_repository_pokeapi import PokemonPokeAPIRepository

router = APIRouter()

repo = PokemonPokeAPIRepository()
use_case = BestCounterUseCase(repo)

class RequestModel(BaseModel):
    pokemons: list[str]
    rival: str

@router.post("/best-counter")
def best_counter(req: RequestModel):
    results = use_case.execute(req.pokemons, req.rival)
    return [
        {
            "name": r.name,
            "types": r.types,
            "attack": r.attack,
            "defense": r.defense,
            "score": r.score,
        }
        for r in results
    ]
