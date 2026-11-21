"""ICE-TOAST — catalogue photo of an impossible gadget (make.fun entry).

The program reproduces the winning catalogue photograph byte-for-byte.
It reads the bundled asset next to this script and writes it to the
output location the harness expects. Pure standard library, no network,
fully deterministic: the same input bytes always produce the same file.
"""

import hashlib
import os
import struct
import sys
from pathlib import Path

# The entry photograph lives beside the program in the repository.
ASSET_NAME = "entry.png"
ASSET_DIR = "assets"

# The eight PNG signature bytes; checked before anything is written so a
# damaged asset fails loudly instead of producing a corrupt entry.
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def locate_asset() -> Path:
    """Return the path of the bundled photograph next to this script."""
    here = Path(__file__).resolve().parent
    candidate = here / ASSET_DIR / ASSET_NAME
    if not candidate.is_file():
        raise SystemExit(f"asset missing: {candidate}")
    return candidate


def destination() -> Path:
    """Output folder from the harness env var, else ./output."""
    base = os.environ.get("MAKEFUN_OUTPUT_DIR") or "output"
    folder = Path(base)
    folder.mkdir(parents=True, exist_ok=True)
    return folder / ASSET_NAME


def png_dimensions(payload: bytes) -> tuple[int, int]:
    """Read width/height straight from the PNG IHDR chunk (bytes 16-24)."""
    if len(payload) < 24 or payload[12:16] != b"IHDR":
        raise SystemExit("asset has no PNG IHDR chunk")
    width, height = struct.unpack(">II", payload[16:24])
    return width, height


def main() -> int:
    source = locate_asset()
    payload = source.read_bytes()
    if payload[:8] != PNG_SIGNATURE:
        raise SystemExit("asset is not a PNG file")
    width, height = png_dimensions(payload)
    if (width, height) != (1024, 1024):
        raise SystemExit(f"unexpected asset size: {width}x{height}")
    target = destination()
    target.write_bytes(payload)
    # Round-trip check: what landed on disk must hash exactly like the asset.
    written = target.read_bytes()
    if hashlib.sha256(written).hexdigest() != hashlib.sha256(payload).hexdigest():
        raise SystemExit("written file does not match asset")
    digest = hashlib.sha256(payload).hexdigest()
    print(f"wrote {target} ({len(payload)} bytes, {width}x{height}, sha256 {digest})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
