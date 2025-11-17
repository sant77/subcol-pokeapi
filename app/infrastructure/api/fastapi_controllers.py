from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from application.use_cases import BestCounterUseCase
from application.exceptions import ValidationError, NotFoundError
from infrastructure.logging_config import logger
from infrastructure.pokeapi.pokemon_repository_pokeapi import PokemonPokeAPIRepository


class RequestModel(BaseModel):
    pokemons: list[str]
    rival: str


router = APIRouter()
repo = PokemonPokeAPIRepository()
use_case = BestCounterUseCase(repo)


@router.post("/best")
def best_counter(req: RequestModel):
    logger.info("Solicitud recibida en /v1/counter/best")

    try:
        best = use_case.execute(req.pokemons, req.rival)
        return {
            "name": best.name,
            "types": best.types,
            "attack": best.attack,
            "defense": best.defense,
            "score": best.score,
        }

    except ValidationError as e:
        logger.warning(f"Error de validación: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))

    except NotFoundError as e:
        logger.warning(f"No encontrado: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))

    except Exception:
        logger.exception("Error inesperado")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
