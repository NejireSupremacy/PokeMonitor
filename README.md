# PokeMonitor

PokeMonitor is a small Python tool that reads the current Pokemon party from a running mGBA emulator session and exports structured data for other tools to consume.
It uses a Lua socket bridge inside mGBA to read game memory. Python then decodes the Gen 3 party data and writes one JSON file per party slot into the `output/` folder.

I need to clarify... I am not that experiencies with Pokemon games and this was a project for fun. There may or not be patches that may be useless since certain scenarios may never happen. Though, these should not cause any issues.

## What It Does

Every 5 seconds, PokeMonitor:

1. Connects to the local mGBA Lua bridge.
2. Reads the full party memory block in one request.
3. Splits that data into the six party slots.
4. Decodes Gen 3 nickname text.
5. Decrypts the Gen 3 Pokemon data substructures.
6. Exports full parsed Pokemon data as JSON, including sprite image metadata.

The exporter keeps updates small. Output files are written through temporary files and then atomically replaced, which helps avoid partial reads from external tools.

Data files update when either of these criteria are met:

1. A Pokemon levels up.
2. A Pokemon changes slot or identity state, such as manually moving party slots, evolving, or otherwise changing which Pokemon belongs in a slot.

## Requirements

- Python 3
- mGBA with Lua scripting support
- Pokemon FireRed or LeafGreen loaded in mGBA
- Python dependencies from `requirements.txt`

Install dependencies from the project root:

```powershell
python -m pip install -r requirements.txt
```

## How To Use

1. Open mGBA and load Pokemon FireRed or LeafGreen.
2. In mGBA, run the Lua bridge script:

```text
lua/mgba_bridge.lua
```

3. In a terminal from the project root, start PokeMonitor:

```powershell
python main.py
```

4. Use the generated files from:

```text
output/
```

## Output Files

For each party slot, PokeMonitor creates:

- `pokemon_x.json`: the parsed Pokemon data for party slot `x`.

Example output layout:

```text
output/
  pokemon_1.json
  pokemon_2.json
  ...
  pokemon_6.json
```

Each JSON file contains the decoded outer party fields, decrypted Growth/Attacks/EVs/Misc data, raw hex data, checksum information, and an `image` object with a sprite URL when the species is known.

Empty party slots export `null`.

## Project Structure

```text
PokeMonitor/
  main.py
  requirements.txt
  README.md
  LICENSE.md
  src/
    __init__.py
    bridge.py
    cli.py
    exporter.py
    gen3_pokemon.py
    gen3_text.py
    memory.py
    team_cache.py
  lua/
    mgba_bridge.lua
  docs/
    memory_notes.md
  output/
    pokemon_1.json
    ...
```

## Notes

- Memory addresses and Gen 3 party structure notes are in `docs/memory_notes.md`.
- The current species-to-sprite map covers the first 151 Pokemon.
- Sprite files are no longer downloaded. JSON exports include a Pokemon Database sprite URL in the `image` object when the species is known.
- The Lua bridge listens on `127.0.0.1:54321` and closes each client connection after handling its command.
- I have not tested this in the long term... It shouldn't have any memory leaks or issues, but I can't guarantee it. If you find any bugs or have suggestions, please open an issue or submit a pull request.

## Credits

- Gen 3 Pokemon memory reference: [Data Crystal](https://datacrystal.tcrf.net/wiki/Pok%C3%A9mon_3rd_Generation/Pok%C3%A9mon_FireRed_and_LeafGreen/RAM_map)
- Gen 3 Pokemon sprites: [Pokemon Database](https://pokemondb.net/sprites)
- AI assistance was used for code formatting, project structure, and maintenance tasks.
