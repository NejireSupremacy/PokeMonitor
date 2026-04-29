GEN3_CHARS = {
    0x00: " ",
    0x2D: "&",
    0x2E: "+",
    0x34: "Lv",
    0x35: "=",
    0x36: ";",
    0x51: "?",
    0x52: "!",
    0x5B: "%",
    0x5C: "(",
    0x5D: ")",
    0x79: "^",
    0x7A: "v",
    0x7B: "<-",
    0x7C: "->",
    0x85: "<",
    0x86: ">",
    0xA0: "e",
    0xAB: "!",
    0xAC: "?",
    0xAD: ".",
    0xAE: "-",
    0xB0: "...",
    0xB1: '"',
    0xB2: '"',
    0xB3: "'",
    0xB4: "'",
    0xB5: "M",
    0xB6: "F",
    0xB7: "$",
    0xB8: ",",
    0xB9: "x",
    0xBA: "/",
    0xF0: ":",
}

GEN3_CHARS.update({code: str(code - 0xA1) for code in range(0xA1, 0xAB)})
GEN3_CHARS.update({code: chr(ord("A") + code - 0xBB) for code in range(0xBB, 0xD5)})
GEN3_CHARS.update({code: chr(ord("a") + code - 0xD5) for code in range(0xD5, 0xEF)})


def decode_gen3_text(data: bytes) -> str:
    letters = []

    for byte in data:
        if byte == 0xFF:
            break
        letters.append(GEN3_CHARS.get(byte, "?"))

    return "".join(letters).strip()
