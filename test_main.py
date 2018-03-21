import pytest


def test_mean():
    from main import mean_hr
    hr_list = [1, 2, 3, 4.4, 99]
    assert mean_hr(hr_list) == pytest.approx(21.88)

def test_parse_times():
    from main import parse_time
    time_list = [[
