import pytest


def test_mean():
    from main import mean_hr
    hr_list = [1, 2, 3, 4.4, 99]
    assert mean_hr(hr_list) == pytest.approx(21.88)
