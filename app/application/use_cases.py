from domain.entities import PokemonEvaluation
from domain.services import compute_attack_score, compute_defense_score
from application.exceptions import ValidationError, NotFoundError
from infrastructure.logging_config import logger


class BestCounterUseCase:
    def __init__(self, repo):
        self.repo = repo
        self.cache = {}

    def execute(self, pokemons: list[str], rival: str) -> PokemonEvaluation:

        if not pokemons or len(pokemons) == 0:
            logger.error("La lista de pokemons está vacía")
            raise ValidationError("Debes enviar al menos un Pokémon.")

        if not rival:
            logger.error("El rival no fue especificado")
            raise ValidationError("Debes especificar el Pokémon rival.")

        try:
            rival_types = self.repo.get_pokemon_types(rival)
        except Exception:
            logger.exception(f"Rival no encontrado: {rival}")
            raise NotFoundError(f"El Pokémon rival '{rival}' no existe.")

        results = []

        for p in pokemons:
            try:
                my_types = self.repo.get_pokemon_types(p)
            except Exception:
                logger.exception(f"Pokémon no encontrado en lista: {p}")
                raise NotFoundError(f"El Pokémon '{p}' no existe.")

            attack = compute_attack_score(my_types, rival_types, self.cache, self.repo)
            defense = compute_defense_score(rival_types, my_types, self.cache, self.repo)
            score = attack - defense

            logger.info(f"Evaluado {p}: score={score}")

            results.append(
                PokemonEvaluation(
                    name=p,
                    types=my_types,
                    attack=attack,
                    defense=defense,
                    score=score
                )
            )

        best = max(results, key=lambda x: x.score)
        logger.info(f"Mejor counter encontrado: {best.name}")
        return best
