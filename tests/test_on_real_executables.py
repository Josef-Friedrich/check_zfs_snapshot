import os
import subprocess
from pathlib import Path


def test_ok() -> None:
    bin_dir = Path(__file__).parent / ".." / "test" / "bin"

    env = os.environ.copy()
    env["PATH"] = str(bin_dir) + ":" + env["PATH"]

    subprocess.run(["zfs", "list ok_dataset"], env=env)
