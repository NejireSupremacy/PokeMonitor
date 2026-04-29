import os
from time import sleep

from src.bridge import read_bytes
from src.gen3_pokemon import format_party_pokemon_full_data, parse_party_pokemon_data
from src.memory import PARTY_POKEMON_SIZE, POKEMON_TEAM
from src.team_cache import TeamCache


def main() -> None:
    team_cache = TeamCache(slot_count=len(POKEMON_TEAM))
    party_slots = list(POKEMON_TEAM.items())
    party_start = min(POKEMON_TEAM.values())
    party_end = max(POKEMON_TEAM.values()) + PARTY_POKEMON_SIZE
    party_length = party_end - party_start

    while True:
        party_data = read_bytes(party_start, party_length)
        team = []

        for slot, pokemon_addr in party_slots:
            offset = pokemon_addr - party_start
            pokemon_data = party_data[offset : offset + PARTY_POKEMON_SIZE]
            team.append(parse_party_pokemon_data(slot, pokemon_data))

        team_cache.sync(team)

        sleep(5)
