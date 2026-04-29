import json
import os

OUTPUT_DIR = "output"
IMG_BASE_URL = "https://img.pokemondb.net/sprites/ruby-sapphire/normal/{}.png"

# TODO: I should really format this data directly rather than cleaning it with string manipulation. But this is good enough for now.
POKEMON_NAME_MAP = {
    1: "Bulbasaur",
    2: "Ivysaur",
    3: "Venusaur",
    4: "Charmander",
    5: "Charmeleon",
    6: "Charizard",
    7: "Squirtle",
    8: "Wartortle",
    9: "Blastoise",
    10: "Caterpie",
    11: "Metapod",
    12: "Butterfree",
    13: "Weedle",
    14: "Kakuna",
    15: "Beedrill",
    16: "Pidgey",
    17: "Pidgeotto",
    18: "Pidgeot",
    19: "Rattata",
    20: "Raticate",
    21: "Spearow",
    22: "Fearow",
    23: "Ekans",
    24: "Arbok",
    25: "Pikachu",
    26: "Raichu",
    27: "Sandshrew",
    28: "Sandslash",
    29: "Nidoran-f",
    30: "Nidorina",
    31: "Nidoqueen",
    32: "Nidoran-m",
    33: "Nidorino",
    34: "Nidoking",
    35: "Clefairy",
    36: "Clefable",
    37: "Vulpix",
    38: "Ninetales",
    39: "Jigglypuff",
    40: "Wigglytuff",
    41: "Zubat",
    42: "Golbat",
    43: "Oddish",
    44: "Gloom",
    45: "Vileplume",
    46: "Paras",
    47: "Parasect",
    48: "Venonat",
    49: "Venomoth",
    50: "Diglett",
    51: "Dugtrio",
    52: "Meowth",
    53: "Persian",
    54: "Psyduck",
    55: "Golduck",
    56: "Mankey",
    57: "Primeape",
    58: "Growlithe",
    59: "Arcanine",
    60: "Poliwag",
    61: "Poliwhirl",
    62: "Poliwrath",
    63: "Abra",
    64: "Kadabra",
    65: "Alakazam",
    66: "Machop",
    67: "Machoke",
    68: "Machamp",
    69: "Bellsprout",
    70: "Weepinbell",
    71: "Victreebel",
    72: "Tentacool",
    73: "Tentacruel",
    74: "Geodude",
    75: "Graveler",
    76: "Golem",
    77: "Ponyta",
    78: "Rapidash",
    79: "Slowpoke",
    80: "Slowbro",
    81: "Magnemite",
    82: "Magneton",
    83: "Farfetchd",
    84: "Doduo",
    85: "Dodrio",
    86: "Seel",
    87: "Dewgong",
    88: "Grimer",
    89: "Muk",
    90: "Shellder",
    91: "Cloyster",
    92: "Gastly",
    93: "Haunter",
    94: "Gengar",
    95: "Onix",
    96: "Drowzee",
    97: "Hypno",
    98: "Krabby",
    99: "Kingler",
    100: "Voltorb",
    101: "Electrode",
    102: "Exeggcute",
    103: "Exeggutor",
    104: "Cubone",
    105: "Marowak",
    106: "Hitmonlee",
    107: "Hitmonchan",
    108: "Lickitung",
    109: "Koffing",
    110: "Weezing",
    111: "Rhyhorn",
    112: "Rhydon",
    113: "Chansey",
    114: "Tangela",
    115: "Kangaskhan",
    116: "Horsea",
    117: "Seadra",
    118: "Goldeen",
    119: "Seaking",
    120: "Staryu",
    121: "Starmie",
    122: "Mr-Mime",
    123: "Scyther",
    124: "Jynx",
    125: "Electabuzz",
    126: "Magmar",
    127: "Pinsir",
    128: "Tauros",
    129: "Magikarp",
    130: "Gyarados",
    131: "Lapras",
    132: "Ditto",
    133: "Eevee",
    134: "Vaporeon",
    135: "Jolteon",
    136: "Flareon",
    137: "Porygon",
    138: "Omanyte",
    139: "Omastar",
    140: "Kabuto",
    141: "Kabutops",
    142: "Aerodactyl",
    143: "Snorlax",
    144: "Articuno",
    145: "Zapdos",
    146: "Moltres",
    147: "Dratini",
    148: "Dragonair",
    149: "Dragonite",
    150: "Mewtwo",
    151: "Mew",
}

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_pokemon_file_paths(slot):
    return [
        os.path.join(OUTPUT_DIR, f"pokemon_{slot}.json"),
    ]


def export_pokemon(pokemon, slot):
    ensure_output_dir()
    write_atomic(
        get_pokemon_file_paths(slot)[0],
        json.dumps(pokemon_to_json_object(pokemon), indent=2, sort_keys=False),
        "w",
        encoding="utf-8",
    )


def pokemon_to_json_object(pokemon):
    if pokemon is None:
        return None

    data = dict(pokemon.full_data)
    species_name = POKEMON_NAME_MAP.get(pokemon.species_id)
    data["image"] = {
        "url": IMG_BASE_URL.format(species_name.lower()) if species_name else None,
        "species_name": species_name,
    }
    return data


def write_atomic(path, data, mode, encoding=None):
    temp_path = f"{path}.tmp"
    if "b" in mode:
        with open(temp_path, mode) as f:
            f.write(data)
    else:
        with open(temp_path, mode, encoding=encoding) as f:
            f.write(data)
    os.replace(temp_path, path)


def move_pokemon_files_to_temp(source_slot, temp_suffix):
    ensure_output_dir()
    temp_paths = []

    for index, source_path in enumerate(get_pokemon_file_paths(source_slot)):
        temp_path = f"{source_path}.{temp_suffix}.tmp"
        if os.path.exists(source_path):
            os.replace(source_path, temp_path)
            temp_paths.append((index, temp_path))

    return temp_paths


def move_temp_pokemon_files(temp_paths, target_slot):
    target_paths = get_pokemon_file_paths(target_slot)

    for index, temp_path in temp_paths:
        target_path = target_paths[index]
        if os.path.exists(temp_path):
            os.replace(temp_path, target_path)
