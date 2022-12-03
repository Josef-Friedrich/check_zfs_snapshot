import unittest


from tests.helper import run
import check_zfs_snapshot


class TestWithSubprocess(unittest.TestCase):
    def test_help(self) -> None:
        process = run(["--help"])
        self.assertEqual(process.returncode, 0)
        self.assertIn("usage: check_zfs_snapshot", process.stdout)

    def test_version(self) -> None:
        process = run(
            ["--version"],
        )
        self.assertEqual(process.returncode, 0)
        self.assertIn(
            "check_zfs_snapshot " + check_zfs_snapshot.__version__, process.stdout
        )


if __name__ == "__main__":
    unittest.main()
