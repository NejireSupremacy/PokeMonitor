from dataclasses import dataclass

from src.exporter import export_pokemon, move_pokemon_files_to_temp, move_temp_pokemon_files
from src.gen3_pokemon import PartyPokemon


@dataclass(frozen=True)
class PokemonSnapshot:
    pid: int
    ot_id: int
    nickname: str
    species_id: int
    level: int

    @classmethod
    def from_party_pokemon(cls, pokemon: PartyPokemon) -> "PokemonSnapshot":
        return cls(
            pid=pokemon.pid,
            ot_id=pokemon.ot_id,
            nickname=pokemon.nickname,
            species_id=pokemon.species_id,
            level=pokemon.full_data["outer"]["level"],
        )

    @property
    def identity_key(self) -> tuple[int, int]:
        return (self.pid, self.ot_id)


class TeamCache:
    def __init__(self, slot_count: int) -> None:
        self.slots: list[PokemonSnapshot | None] = [None] * slot_count
        self.initialized = False

    def sync(self, team: list[PartyPokemon | None]) -> None:
        current = [
            PokemonSnapshot.from_party_pokemon(pokemon) if pokemon else None
            for pokemon in team
        ]

        if len(current) != len(self.slots):
            raise ValueError("Team size does not match cache size.")

        if not self.initialized:
            for slot, pokemon in enumerate(team, start=1):
                export_pokemon(pokemon, slot)

            self.slots = current
            self.initialized = True
            return

        previous_by_identity = {
            pokemon.identity_key: slot
            for slot, pokemon in enumerate(self.slots)
            if pokemon is not None
        }
        move_map: dict[int, int] = {}
        full_export_slots: set[int] = set()
        clear_slots: set[int] = set()

        for slot, pokemon in enumerate(current):
            previous_pokemon = self.slots[slot]

            if pokemon is None:
                if previous_pokemon is not None:
                    clear_slots.add(slot)
                continue

            if pokemon == previous_pokemon:
                continue

            previous_slot = previous_by_identity.get(pokemon.identity_key)
            if (
                previous_slot is not None
                and previous_slot != slot
                and self.slots[previous_slot] == pokemon
            ):
                move_map[previous_slot] = slot
                continue

            if (
                previous_pokemon is not None
                and pokemon.identity_key == previous_pokemon.identity_key
                and pokemon.species_id == previous_pokemon.species_id
            ):
                full_export_slots.add(slot)
                continue

            full_export_slots.add(slot)

        temp_moves = {
            source_slot: move_pokemon_files_to_temp(source_slot + 1, f"slot{source_slot + 1}")
            for source_slot in move_map
        }

        for source_slot, target_slot in move_map.items():
            move_temp_pokemon_files(temp_moves[source_slot], target_slot + 1)

        for slot in full_export_slots:
            export_pokemon(team[slot], slot + 1)

        for slot in clear_slots:
            export_pokemon(None, slot + 1)

        self.slots = current
