import requests
from domain.ports import PokemonRepository

POKEAPI = "https://pokeapi.co/api/v2"

class PokemonPokeAPIRepository(PokemonRepository):

    def get_pokemon_types(self, name):
        r = requests.get(f"{POKEAPI}/pokemon/{name.lower()}")
        data = r.json()
        return [t["type"]["name"] for t in data["types"]]

    def get_type_relations(self, type_name):
        r = requests.get(f"{POKEAPI}/type/{type_name.lower()}")
        data = r.json()
        rel = data["damage_relations"]

        def extract(list_obj):
            return [x["name"] for x in list_obj]

        return {
            "double_to": extract(rel["double_damage_to"]),
            "half_to": extract(rel["half_damage_to"]),
            "no_to": extract(rel["no_damage_to"]),
            "double_from": extract(rel["double_damage_from"]),
            "half_from": extract(rel["half_damage_from"]),
            "no_from": extract(rel["no_damage_from"]),
        }
