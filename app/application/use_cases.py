from domain.entities import PokemonEvaluation
from domain.services import compute_attack_score, compute_defense_score

class BestCounterUseCase:
    def __init__(self, repo):
        self.repo = repo
        self.cache = {}

    def execute(self, pokemons: list[str], rival: str):
        rival_types = self.repo.get_pokemon_types(rival)

        results = []

        for p in pokemons:
            my_types = self.repo.get_pokemon_types(p)

            attack = compute_attack_score(my_types, rival_types, self.cache, self.repo)
            defense = compute_defense_score(rival_types, my_types, self.cache, self.repo)

            score = attack - defense

            results.append(
                PokemonEvaluation(
                    name=p,
                    types=my_types,
                    attack=attack,
                    defense=defense,
                    score=score
                )
            )

        # Ordenar por score mayor
        results.sort(key=lambda x: x.score, reverse=True)

        return results
