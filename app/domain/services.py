def type_factor(attacker_type, defender_type, type_relations_cache, repo):
    if defender_type not in type_relations_cache:
        type_relations_cache[defender_type] = repo.get_type_relations(defender_type)

    rel = type_relations_cache[defender_type]

    if attacker_type in rel["no_from"]:
        return 0        
    if attacker_type in rel["double_from"]:
        return 2       
    if attacker_type in rel["half_from"]:
        return 0.5      
    return 1


def compute_attack_score(attacker_types, defender_types, cache, repo):
    best = 0
    for atk in attacker_types:
        multiplier = 1
        for d in defender_types:
            multiplier *= type_factor(atk, d, cache, repo)
        best = max(best, multiplier)
    return best


def compute_defense_score(attacker_types, defender_types, cache, repo):
    worst = 0
    for atk in attacker_types:
        multiplier = 1
        for d in defender_types:
            multiplier *= type_factor(atk, d, cache, repo)
        worst = max(worst, multiplier)
    return worst
