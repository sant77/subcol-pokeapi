import requests
from domain.ports import PokemonRepository

POKEAPI = "https://pokeapi.co/api/v2"

# -------------------------------
#  CACHE GLOBAL
# -------------------------------
POKEMON_TYPES_CACHE = {}
TYPE_RELATIONS_CACHE = {}


class PokemonPokeAPIRepository(PokemonRepository):

    def get_pokemon_types(self, name):
        name = name.lower()

        # CACHE HIT
        if name in POKEMON_TYPES_CACHE:
            return POKEMON_TYPES_CACHE[name]

        # CACHE MISS → llamar API
        r = requests.get(f"{POKEAPI}/pokemon/{name}")
        data = r.json()

        types = [t["type"]["name"] for t in data["types"]]

        # Guardar en caché
        POKEMON_TYPES_CACHE[name] = types

        return types

    def get_type_relations(self, type_name):
        type_name = type_name.lower()

        # CACHE HIT
        if type_name in TYPE_RELATIONS_CACHE:
            return TYPE_RELATIONS_CACHE[type_name]

        # CACHE MISS → llamar API
        r = requests.get(f"{POKEAPI}/type/{type_name}")
        data = r.json()
        rel = data["damage_relations"]

        def extract(list_obj):
            return [x["name"] for x in list_obj]

        relations = {
            "double_to": extract(rel["double_damage_to"]),
            "half_to": extract(rel["half_damage_to"]),
            "no_to": extract(rel["no_damage_to"]),
            "double_from": extract(rel["double_damage_from"]),
            "half_from": extract(rel["half_damage_from"]),
            "no_from": extract(rel["no_damage_from"]),
        }

        # Guardar en caché
        TYPE_RELATIONS_CACHE[type_name] = relations

        return relations
