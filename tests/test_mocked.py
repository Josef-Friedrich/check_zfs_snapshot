from unittest.mock import Mock, patch

from check_zfs_snapshot import _count_snapshots, _list_datasets  # type: ignore


@patch("check_zfs_snapshot.subprocess.check_output")
def test_list_datasets(mock_run: Mock) -> None:
    mock_run.return_value = """data	7.82T	2.62T	67.7G	/data
data/archive	592G	2.62T	39.5G	/data/archive
data/document	5.41G	2.62T	1.94G	/data/document
"""
    assert ["data", "data/archive", "data/document"] == _list_datasets()


@patch("check_zfs_snapshot.subprocess.check_output")
def test_count_snapshots(mock_run: Mock) -> None:
    mock_run.return_value = """
data/trash/video@zfs-auto-snap_hourly-2026-01-31-1500	0	-	166656	-
data/video@20140519	238080	-	71493953856	-
data/video@20140720	249984	-	74830746240	-
data/video@zfs-auto-snap_monthly-2014-11-23-2046	190464	-	75150196032	-
"""
    assert 1 == _count_snapshots("data/trash/video")
    assert 0 == _count_snapshots("trash/video")
    assert 3 == _count_snapshots("data/video")
