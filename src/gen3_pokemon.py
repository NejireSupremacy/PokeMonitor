import json
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
    full_data: dict


def decrypt_pokemon_data(pid: int, ot_id: int, data: bytes) -> bytes:
    key = pid ^ ot_id
    decrypted = bytearray()

    for i in range(0, PARTY_POKEMON_ENCRYPTED_LENGTH, 4):
        chunk = int.from_bytes(data[i : i + 4], "little")
        decrypted.extend((chunk ^ key).to_bytes(4, "little"))

    return bytes(decrypted)


def get_growth_block(pid: int, decrypted: bytes) -> bytes:
    return get_data_blocks(pid, decrypted)["growth"]


def get_data_blocks(pid: int, decrypted: bytes) -> dict[str, bytes]:
    blocks = [
        decrypted[i : i + PARTY_POKEMON_BLOCK_SIZE]
        for i in range(0, PARTY_POKEMON_ENCRYPTED_LENGTH, PARTY_POKEMON_BLOCK_SIZE)
    ]
    block_order = BLOCK_ORDERS[pid % 24]
    block_map = {block_order[i]: blocks[i] for i in range(4)}
    return {
        "growth": block_map["G"],
        "attacks": block_map["A"],
        "evs_condition": block_map["E"],
        "misc": block_map["M"],
    }


def _u16(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "little")


def _u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def _hex(data: bytes) -> str:
    return data.hex(" ")


def calculate_data_checksum(decrypted: bytes) -> int:
    return sum(_u16(decrypted, i) for i in range(0, len(decrypted), 2)) & 0xFFFF


def parse_party_pokemon_full_data(slot: int, data: bytes) -> dict | None:
    if len(data) < PARTY_POKEMON_SIZE:
        raise ValueError("Party Pokemon data is too short.")

    pid = _u32(data, 0)
    ot_id = _u32(data, 4)

    if pid == 0 and ot_id == 0:
        return None

    encrypted_data = data[
        PARTY_POKEMON_DATA_OFFSET : PARTY_POKEMON_DATA_OFFSET
        + PARTY_POKEMON_ENCRYPTED_LENGTH
    ]
    decrypted = decrypt_pokemon_data(pid, ot_id, encrypted_data)
    blocks = get_data_blocks(pid, decrypted)
    growth = blocks["growth"]
    attacks = blocks["attacks"]
    evs_condition = blocks["evs_condition"]
    misc = blocks["misc"]
    stored_checksum = _u16(data, 0x1C)
    calculated_checksum = calculate_data_checksum(decrypted)

    return {
        "slot": slot,
        "outer": {
            "pid": pid,
            "ot_id": ot_id,
            "nickname": decode_gen3_text(data[8:18]),
            "language": data[0x12],
            "misc_flags": data[0x13],
            "ot_name": decode_gen3_text(data[0x14:0x1B]),
            "markings": data[0x1B],
            "checksum": stored_checksum,
            "calculated_checksum": calculated_checksum,
            "checksum_valid": stored_checksum == calculated_checksum,
            "unknown": _u16(data, 0x1E),
            "status_condition": _u32(data, 0x50),
            "level": data[0x54],
            "mail_id": data[0x55],
            "current_hp": _u16(data, 0x56),
            "max_hp": _u16(data, 0x58),
            "attack": _u16(data, 0x5A),
            "defense": _u16(data, 0x5C),
            "speed": _u16(data, 0x5E),
            "sp_attack": _u16(data, 0x60),
            "sp_defense": _u16(data, 0x62),
        },
        "encrypted_data": {
            "key": pid ^ ot_id,
            "block_order": BLOCK_ORDERS[pid % 24],
            "raw_hex": _hex(encrypted_data),
            "decrypted_hex": _hex(decrypted),
        },
        "growth": {
            "species_id": _u16(growth, 0),
            "held_item_id": _u16(growth, 2),
            "experience": _u32(growth, 4),
            "pp_bonuses": growth[8],
            "friendship": growth[9],
            "unused": _u16(growth, 10),
        },
        "attacks": {
            "move_ids": [_u16(attacks, i) for i in range(0, 8, 2)],
            "pp": list(attacks[8:12]),
        },
        "evs_condition": {
            "hp_ev": evs_condition[0],
            "attack_ev": evs_condition[1],
            "defense_ev": evs_condition[2],
            "speed_ev": evs_condition[3],
            "sp_attack_ev": evs_condition[4],
            "sp_defense_ev": evs_condition[5],
            "coolness": evs_condition[6],
            "beauty": evs_condition[7],
            "cuteness": evs_condition[8],
            "smartness": evs_condition[9],
            "toughness": evs_condition[10],
            "feel": evs_condition[11],
        },
        "misc": {
            "pokerus_status": misc[0],
            "met_location": misc[1],
            "origins_info": _u16(misc, 2),
            "ivs_egg_ability": _u32(misc, 4),
            "ribbons_obedience": _u32(misc, 8),
        },
        "raw_party_data_hex": _hex(data[:PARTY_POKEMON_SIZE]),
    }


def format_party_pokemon_full_data(slot: int, data: bytes) -> str:
    return json.dumps(
        parse_party_pokemon_full_data(slot, data),
        indent=2,
        sort_keys=False,
    )


def parse_party_pokemon_data(slot: int, data: bytes) -> PartyPokemon | None:
    if len(data) < PARTY_POKEMON_SIZE:
        raise ValueError("Party Pokemon data is too short.")

    pid = int.from_bytes(data[0:4], "little")
    ot_id = int.from_bytes(data[4:8], "little")

    if pid == 0 and ot_id == 0:
        return None

    full_data = parse_party_pokemon_full_data(slot, data)
    if full_data is None:
        return None

    return PartyPokemon(
        slot=slot,
        pid=pid,
        ot_id=ot_id,
        nickname=full_data["outer"]["nickname"],
        species_id=full_data["growth"]["species_id"],
        full_data=full_data,
    )


def parse_party_pokemon(slot: int, address: int, read32, read_bytes) -> PartyPokemon | None:
    return parse_party_pokemon_data(slot, read_bytes(address, PARTY_POKEMON_SIZE))
