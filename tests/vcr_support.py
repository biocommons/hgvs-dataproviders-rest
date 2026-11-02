import os
from pathlib import Path

import vcr as vcrpy

test_data_dir = Path(__file__).parent / "cassettes"

vcr = vcrpy.VCR(
    cassette_library_dir=str(test_data_dir),
    record_mode=os.environ.get("VCR_RECORD_MODE", "new_episodes"),
)
