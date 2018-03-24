import pytest
import datetime
import jsonschema


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
    t = '2008-12-24 01:23:33.000231'

    assert hr_mean_since(hr_list, dt_list, t)


def test_json_validation():
    from main import validate_user_json

    json = {
        "user_email": "suyash@suyashkumar.com",
        "user_age": 50,
        "heart_rate": 100
    }

    validate_user_json(json)

    json = {
        "user_email": "not_an_email",
        "user_age": 50,
        "heart_rate": 100
    }

    with pytest.raises(jsonschema.ValidationError):
        validate_user_json(json)

    json = {
        "user_email": "edl13@duke.edu",
        "user_age": 'wow',
        "heart_rate": 100
    }

    with pytest.raises(jsonschema.ValidationError):
        validate_user_json(json)

    json = {
        "user_email": "edl13@duke.edu",
    }

    with pytest.raises(jsonschema.ValidationError):
        validate_user_json(json)

    from main import validate_hr_post_json

    json = {
        'user_email': 'edl13@duke.edu',
        'heart_rate_average_since': '2018-03-09 11:00:36.372339'
    }

    validate_hr_post_json(json)

    json = {
        'user_email': 'edl13@duke.edu',
        'heart_rate_average_since': '2018-03-09 11:00.372339'
    }

    with pytest.raises(jsonschema.ValidationError):
        validate_hr_post_json(json)

    json = {
        'heart_rate_average_since': '2018-03-09 11:00.372339'
    }

    with pytest.raises(jsonschema.ValidationError):
        validate_hr_post_json(json)


def test_tachy():
    from main import check_tachy
    age = [12, 1, 7, 15]
    hr = [112, 200, 90, 120]
    result = [False, True, False, True]

    for i, age in enumerate(age):
        assert check_tachy(hr[i], age) == result[i]
