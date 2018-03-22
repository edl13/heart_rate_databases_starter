import pytest
import datetime


def test_mean():
    from main import mean_hr
    hr_list = [1, 2, 3, 4.4, 99]
    assert mean_hr(hr_list) == pytest.approx(21.88)


def test_parse_time_str():
    from main import parse_time_str
    time_str = "2018-03-09 11:00:36.372339"
    dt = parse_time_str(time_str)
    assert dt.second == 36


def test_mean_since():
    from main import hr_mean_since
    dt_list = [datetime.datetime(1999, 12, 1), datetime.datetime(2001, 11, 14),
               datetime.datetime(2009, 1, 22), datetime.datetime(2010, 5, 12),
               datetime.datetime(2018, 4, 18)]
    hr_list = [55, 66, 70, 55, 100]
    t = '2008-24-12 01:23:33.000231'

    assert hr_mean_since(hr_list, dt_list, t)
