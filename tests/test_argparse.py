import check_zfs_snapshot
from tests.helper import run


class TestWithSubprocess:
    def test_help(self) -> None:
        process = run(["--help"])
        assert process.returncode == 0
        assert "usage: check_zfs_snapshot" in process.stdout

    def test_version(self) -> None:
        process = run(
            ["--version"],
        )
        assert process.returncode == 0
        assert "check_zfs_snapshot " + check_zfs_snapshot.__version__ in process.stdout

    def test_critical_lower_warning(self) -> None:
        process = run(
            ["-c", "1", "-w", "2"],
        )
        assert process.returncode == 1
        assert (
            "ValueError: -w SECONDS must be smaller than -c SECONDS. -w 2 > -c 1"
            in process.stderr
        )
