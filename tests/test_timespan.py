from datetime import datetime

import pytest

from check_zfs_snapshot import Timespan


class TestTimespanInit:
    def test_init_with_none_values(self) -> None:
        ts = Timespan(None, None)
        assert isinstance(ts.start, datetime)
        assert isinstance(ts.end, datetime)

    def test_init_with_int_timestamp(self) -> None:
        ts = Timespan(1000, 2000)
        assert ts.start == datetime.fromtimestamp(1000)
        assert ts.end == datetime.fromtimestamp(2000)

    def test_init_with_float_timestamp(self) -> None:
        ts = Timespan(1000.5, 2000.5)
        assert ts.start == datetime.fromtimestamp(1000.5)
        assert ts.end == datetime.fromtimestamp(2000.5)

    def test_init_with_datetime_objects(self) -> None:
        dt1 = datetime(2020, 1, 1, 12, 0, 0)
        dt2 = datetime(2020, 1, 2, 12, 0, 0)
        ts = Timespan(dt1, dt2)
        assert ts.start == dt1
        assert ts.end == dt2

    def test_init_with_none_end(self) -> None:
        ts = Timespan(1000, None)
        assert ts.start == datetime.fromtimestamp(1000)
        assert isinstance(ts.end, datetime)


class TestTimespan:
    def test_timespan_calculation(self) -> None:
        ts = Timespan(1000, 2000)
        assert ts.timespan == 1000.0

    def test_timespan_with_datetime(self) -> None:
        dt1 = datetime(2020, 1, 1, 12, 0, 0)
        dt2 = datetime(2020, 1, 1, 13, 0, 0)
        ts = Timespan(dt1, dt2)
        assert ts.timespan == 3600.0


class TestTimespanComparison:
    ts = Timespan(1000, 2000)
    # 1000

    def test_timespan(self) -> None:
        assert self.ts.timespan == 1000.0

    def test_lt(self) -> None:
        assert self.ts < 1500
        assert not (self.ts < 500)

    def test_le(self) -> None:
        assert self.ts <= 1000
        assert self.ts <= 1500
        assert not (self.ts <= 500)

    def test_eq_true(self) -> None:
        assert self.ts == 1000
        assert not (self.ts == 500)

    def test_ne_true(self) -> None:
        assert self.ts != 500
        assert not (self.ts != 1000)

    def test_ge_true(self) -> None:
        assert self.ts >= 1000
        assert self.ts >= 500
        assert not (self.ts >= 1500)

    def test_gt_true(self) -> None:
        assert self.ts > 500
        assert not (self.ts > 1000)

    def test_comparison_with_invalid_type(self) -> None:
        ts = Timespan(1000, 2000)
        with pytest.raises(ValueError):
            ts < "string"  # type: ignore


class TestTimespanConversions:
    def test_float(self) -> None:
        ts = Timespan(1000, 2500)
        assert float(ts) == 1500.0

    def test_int(self) -> None:
        ts = Timespan(1000, 2500)
        assert int(ts) == 1500

    def test_int_rounding(self) -> None:
        ts = Timespan(1000, 2600)
        assert isinstance(int(ts), int)

    def test_str(self) -> None:
        ts = Timespan(1000, 2600)
        assert str(ts) == "1970-01-01T01:16:40 - 1970-01-01T01:43:20"
