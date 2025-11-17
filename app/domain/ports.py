from abc import ABC, abstractmethod

class PokemonRepository(ABC):
    @abstractmethod
    def get_pokemon_types(self, name: str) -> list[str]:
        pass

    @abstractmethod
    def get_type_relations(self, type_name: str) -> dict:
        pass