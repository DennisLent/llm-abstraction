import json
import hashlib
from pathlib import Path

def map_to_filename(world: list[list[str]], extension: str = None) -> str:
    """Generate a deterministic filename for a map.

    The 2D grid is serialized to JSON and hashed with SHA-1. The first
    ten hex digits of the hash are used for brevity.

    Parameters
    ----------
    world : list of list of str
        2D character grid representing the map.
    extension : str, optional
        Optional filename extension to append, including the leading dot.

    Returns
    -------
    str
        A filename of the form ``map_{rows}x{cols}_{hash}[extension]``.

    Raises
    ------
    ValueError
        If ``world`` is ``None``.
    """
    if world is None:
        raise ValueError("Missing world to generate hash name")
    
    s = json.dumps(world, separators=(",", ":"), ensure_ascii=False)

    # SHA-1 generates 40 hexadecimal characters (160 bits).
    # Truncating to 10 hex characters provides a very low collision risk
    # at typical dataset sizes while keeping filenames short.
    h = hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]


    rows, cols = len(world), len(world[0])
    if extension is None:
        return f"map_{rows}x{cols}_{h}"
    else:
        return f"map_{rows}x{cols}_{h}{extension}"
