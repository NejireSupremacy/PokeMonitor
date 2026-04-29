from dataclasses import dataclass

from src.gen3_text import decode_gen3_text
from src.memory import (
    PARTY_POKEMON_BLOCK_SIZE,
    PARTY_POKEMON_DATA_OFFSET,
    PARTY_POKEMON_ENCRYPTED_LENGTH,
    PARTY_POKEMON_SIZE,
)

BLOCK_ORDERS = [
    "GAEM",
    "GAME",
    "GEAM",
    "GEMA",
    "GMAE",
    "GMEA",
    "AGEM",
    "AGME",
    "AEGM",
    "AEMG",
    "AMGE",
    "AMEG",
    "EGAM",
    "EGMA",
    "EAGM",
    "EAMG",
    "EMGA",
    "EMAG",
    "MGAE",
    "MGEA",
    "MAGE",
    "MAEG",
    "MEGA",
    "MEAG",
]


@dataclass(frozen=True)
class PartyPokemon:
    slot: int
    pid: int
    ot_id: int
    nickname: str
    species_id: int


def decrypt_pokemon_data(pid: int, ot_id: int, data: bytes) -> bytes:
    key = pid ^ ot_id
    decrypted = bytearray()

    for i in range(0, PARTY_POKEMON_ENCRYPTED_LENGTH, 4):
        chunk = int.from_bytes(data[i : i + 4], "little")
        decrypted.extend((chunk ^ key).to_bytes(4, "little"))

    return bytes(decrypted)


def get_growth_block(pid: int, decrypted: bytes) -> bytes:
    blocks = [
        decrypted[i : i + PARTY_POKEMON_BLOCK_SIZE]
        for i in range(0, PARTY_POKEMON_ENCRYPTED_LENGTH, PARTY_POKEMON_BLOCK_SIZE)
    ]
    block_order = BLOCK_ORDERS[pid % 24]
    block_map = {block_order[i]: blocks[i] for i in range(4)}
    return block_map["G"]


def parse_party_pokemon_data(slot: int, data: bytes) -> PartyPokemon | None:
    if len(data) < PARTY_POKEMON_SIZE:
        raise ValueError("Party Pokemon data is too short.")

    pid = int.from_bytes(data[0:4], "little")
    ot_id = int.from_bytes(data[4:8], "little")

    if pid == 0 and ot_id == 0:
        return None

    nickname = decode_gen3_text(data[8:18])
    encrypted_data = data[
        PARTY_POKEMON_DATA_OFFSET : PARTY_POKEMON_DATA_OFFSET
        + PARTY_POKEMON_ENCRYPTED_LENGTH
    ]
    decrypted = decrypt_pokemon_data(pid, ot_id, encrypted_data)
    growth = get_growth_block(pid, decrypted)
    species_id = int.from_bytes(growth[0:2], "little")

    return PartyPokemon(
        slot=slot,
        pid=pid,
        ot_id=ot_id,
        nickname=nickname,
        species_id=species_id,
    )


def parse_party_pokemon(slot: int, address: int, read32, read_bytes) -> PartyPokemon | None:
    return parse_party_pokemon_data(slot, read_bytes(address, PARTY_POKEMON_SIZE))
