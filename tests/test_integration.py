from tests.helper import execute_main as main


def test_first_ok_zpool() -> None:
    result = main(["--dataset", "ok_dataset"])
    assert result.exitcode == 0
    assert result.stdout
    assert (
        "ZFS_SNAPSHOT OK | last_snapshot__ok_dataset=1502914537 snapshot_count__ok_dataset=3"
        == result.first_line
    )
