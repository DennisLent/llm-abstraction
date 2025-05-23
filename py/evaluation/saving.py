import json
import hashlib
from pathlib import Path

def map_to_filename(world: list[list[str]], extension: str = None) -> str:
    """
    Turn a 2D char‐grid into a unique filename by:
      1) serializing it to JSON (guaranteed same string each time for the same grid)
      2) hashing with SHA-1
      3) taking the first N hex digits for brevity
    """
    if world is None:
        raise ValueError("Missing world to generate hash name")
    
    s = json.dumps(world, separators=(",", ":"), ensure_ascii=False)

    # Hash generates 40 hexademical characters i.e. 160 bits
    # For 1_000 maps, 32 bits is only 1.2e-7 collision probability
    # For 1_000_000 maps, 40 bits is only 4.5e-7 collision probability
    # 10 bits should be plenty
    h = hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]


    rows, cols = len(world), len(world[0])
    if extension is None:
        return f"map_{rows}x{cols}_{h}"
    else:
        return f"map_{rows}x{cols}_{h}{extension}"