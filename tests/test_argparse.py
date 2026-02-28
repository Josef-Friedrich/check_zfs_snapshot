from argparse import ArgumentParser, Namespace

import check_zfs_snapshot
from check_zfs_snapshot import get_argparser
from tests.helper import run


class TestWithSubprocess:
    def test_help(self) -> None:
        process = run(["--help"])
        assert process.returncode == 3
        assert "usage: check_zfs_snapshot" in process.stdout

    def test_version(self) -> None:
        process = run(
            ["--version"],
        )
        assert process.returncode == 3
        assert "check_zfs_snapshot " + check_zfs_snapshot.__version__ in process.stdout

    def test_critical_lower_warning(self) -> None:
        process = run(
            ["-c", "1", "-w", "2"],
        )
        assert process.returncode == 3
        assert (
            "ValueError: -w SECONDS must be smaller than -c SECONDS. -w 2.0 > -c 1.0"
            in process.stdout
        )


parser: ArgumentParser = get_argparser()


def args(*args: str) -> Namespace:
    return parser.parse_args(args)


class TestMethod:
    class TestDataset:
        def test_none(self) -> None:
            assert args().dataset is None

        def test_long_option(self) -> None:
            assert args("--dataset", "test-dataset").dataset == "test-dataset"

        def test_short_option(self) -> None:
            assert args("-d", "test-dataset").dataset == "test-dataset"

    class TestWarning:
        def test_int(self) -> None:
            assert args("--warning", "42").warning == 42

        def test_timespan(self) -> None:
            assert args("--warning", "1s1m").warning == 61

    class TestCritical:
        def test_int(self) -> None:
            assert args("--critical", "123").critical == 123

        def test_critical_timespan(self) -> None:
            assert args("--critical", "1 min").critical == 60

    class TestVerbose:
        def test_zero(self) -> None:
            assert args().verbose == 0

        def test_one(self) -> None:
            assert args("-v").verbose == 1

        def test_two(self) -> None:
            assert args("-vv").verbose == 2

        def test_three(self) -> None:
            assert args("-vvv").verbose == 3
