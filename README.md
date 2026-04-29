# PokeMonitor

PokeMonitor is a small Python tool that reads the current Pokemon party from a running mGBA emulator session and exports overlay-friendly files for stream layouts, recordings, or other live displays.
It uses a Lua socket bridge inside mGBA to read game memory. Python then decodes the Gen 3 party data and writes each slot's nickname and sprite into the `output/` folder.

I need to clarify... I am not that experiencies with Pokemon games and this was a project for fun. There may or not be patches that may be useless since certain scenarios may never happen. Though, these should not cause any issues.

## What It Does

Every 5 seconds, PokeMonitor:

1. Connects to the local mGBA Lua bridge.
2. Reads the full party memory block in one request.
3. Splits that data into the six party slots.
4. Decodes Gen 3 nickname text.
5. Decrypts the party Pokemon data needed to identify the species.
6. Exports nickname text files and Pokemon sprite PNG files.

The exporter keeps updates small. If only a nickname changes, it rewrites only the text file for that slot instead of downloading the sprite again. Output files are written through temporary files and then atomically replaced, which helps avoid partial reads from tools such as OBS.

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

- `pokemon_name_x.txt`: the nickname for the Pokemon in slot `x`.
- `pokemon_image_x.png`: the sprite image for the Pokemon in slot `x`.

Example output layout:

```text
output/
  pokemon_name_1.txt
  pokemon_image_1.png
  pokemon_name_2.txt
  pokemon_image_2.png
  ...
  pokemon_name_6.txt
  pokemon_image_6.png
```

Empty party slots export an empty text file and an empty image file.

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
    pokemon_name_1.txt
    pokemon_image_1.png
    ...
```

## Notes

- Memory addresses and Gen 3 party structure notes are in `docs/memory_notes.md`.
- The current species-to-sprite map covers the first 151 Pokemon.
- Sprites are downloaded from Pokemon Database when a slot needs a new image.
- The Lua bridge listens on `127.0.0.1:54321` and closes each client connection after handling its command.
- I have not tested this in the long term... It shouldn't have any memory leaks or issues, but I can't guarantee it. If you find any bugs or have suggestions, please open an issue or submit a pull request.

## Credits

- Gen 3 Pokemon memory reference: [Data Crystal](https://datacrystal.tcrf.net/wiki/Pok%C3%A9mon_3rd_Generation/Pok%C3%A9mon_FireRed_and_LeafGreen/RAM_map)
- Gen 3 Pokemon sprites: [Pokemon Database](https://pokemondb.net/sprites)
- AI assistance was used for code formatting, project structure, and maintenance tasks.
