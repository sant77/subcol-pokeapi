import requests

POKEAPI = "https://pokeapi.co/api/v2"


def get_pokemon_types(name):
    """Devuelve una lista de tipos del Pokémon."""
    r = requests.get(f"{POKEAPI}/pokemon/{name}")
    data = r.json()
    return [t["type"]["name"] for t in data["types"]]


def get_type_relations(type_name):
    """Devuelve las relaciones de daño de un tipo."""
    r = requests.get(f"{POKEAPI}/type/{type_name}")
    data = r.json()
    rel = data["damage_relations"]

    # Convertir de listas de objetos a listas de strings (solo nombres)
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


def type_factor(attacker_type, defender_type, types_cache):
    """
    Factor de daño que un tipo atacante hace a un tipo defensor.
    Usa los datos almacenados en types_cache para evitar repetir peticiones.
    """
    if defender_type not in types_cache:
        types_cache[defender_type] = get_type_relations(defender_type)

    rel = types_cache[defender_type]

    if attacker_type in rel["no_from"]:
        return 0        # Inmune
    if attacker_type in rel["double_from"]:
        return 2        # Recibe doble
    if attacker_type in rel["half_from"]:
        return 0.5      # Recibe la mitad
    return 1


def compute_attack_score(attacker_types, defender_types, types_cache):
    """Devuelve el mejor multiplicador de ataque de un Pokémon."""
    best = 0
    for atk in attacker_types:
        multiplier = 1
        for d in defender_types:
            multiplier *= type_factor(atk, d, types_cache)
        best = max(best, multiplier)
    return best


def compute_defense_score(attacker_types, defender_types, types_cache):
    """
    El rival ataca: calcular cuánto daño recibiría el Pokémon.
    attacker_types = tipos del rival
    defender_types = tipos del Pokémon propio
    """
    worst = 0
    for atk in attacker_types:
        multiplier = 1
        for d in defender_types:
            multiplier *= type_factor(atk, d, types_cache)
        worst = max(worst, multiplier)
    return worst


def evaluate_pokemon(name, rival_types, types_cache):
    """Devuelve (name, ataque, defensa, score_final)."""
    my_types = get_pokemon_types(name)

    ataque = compute_attack_score(my_types, rival_types, types_cache)
    defensa = compute_defense_score(rival_types, my_types, types_cache)

    score = ataque - defensa

    return {
        "name": name,
        "types": my_types,
        "ataque": ataque,
        "defensa": defensa,
        "score": score,
    }


def best_counter(pokemons, rival):
    """
    pokemons: lista de nombres de Pokémon propios
    rival: nombre del Pokémon rival
    """
    types_cache = {}

    rival_types = get_pokemon_types(rival)

    results = []
    for p in pokemons:
        results.append(evaluate_pokemon(p, rival_types, types_cache))

    # Ordenar por score mayor
    results.sort(key=lambda x: x["score"], reverse=True)

    return results


# ------------------------------
# EJECUCIÓN CON TU EJEMPLO
# ------------------------------

pokemons = ["pikachu", "gengar", "dragonite"]
rival = "tyranitar"

results = best_counter(pokemons, rival)

for r in results:
    print(f"{r['name']}: tipos={r['types']} ataque={r['ataque']} defensa={r['defensa']} score={r['score']}")
