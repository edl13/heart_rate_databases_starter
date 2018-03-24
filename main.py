import jsonschema
import numpy as np
from pymodm import connect
import models
import datetime
from flask import Flask, jsonify, request
from pymodm.errors import DoesNotExist
app = Flask(__name__)

connect("mongodb://vcm-3582.vm.duke.edu:27017/heart_rate_app")


@app.route('/api/heart_rate', methods=['POST'])
def post_hr_data():
    '''Posts HR data to Mongo database. If user exists, appends HR and
    timestamp to respective list

    :params json: JSON string with email, name, heart rate, and timestamp'''
    json = request.get_json()
    email = json['user_email']

    response = ''

    validate_user_json(json)

    try:
        add_heart_rate(email, json['heart_rate'], datetime.datetime.now())
        response = 'Appended heart rate to {}'.format(email)
    except DoesNotExist:
        create_user(email, json['age'], json['heart_rate'],
                    datetime.datetime.now())
        response = 'Created new user {}'.format(email)
    return response


@app.route('/api/heart_rate/<user_email>', methods=['GET'])
def get_hr_data(user_email):
    '''Gets HR list from Mongo database

    :params user_email: Route variable of user email (primary ID)'''

    user = models.User.objects.raw({'_id': user_email}).first()
    heart_rate_list = user.heart_rate
    print(heart_rate_list)
    return jsonify({'heart_rate': heart_rate_list})


@app.route('/api/heart_rate/average/<user_email>', methods=['GET'])
def get_avg_hr(user_email):
    '''Gets average HR of user

    :params user_email: Route variable of user email (primary ID)'''

    user = models.User.objects.raw({'_id': user_email}).first()
    heart_rate_list = user.heart_rate
    mean = mean_hr(heart_rate_list)
    return jsonify({'Mean_HR': mean, 'times': user.heart_rate_times})


@app.route('/api/heart_rate/interval_average', methods=['POST'])
def get_interval_avg_hr():
    '''Get average HR since time in posted JSON'''

    json = request.get_json()

    validate_hr_post_json(json)

    email = json['user_email']
    user = models.User.objects.raw({'_id': email}).first()
    age = user.age
    heart_rate_list = user.heart_rate
    time_list = user.heart_rate_times
    time_since = json['heart_rate_average_since']
    mean = hr_mean_since(heart_rate_list, time_list, time_since)
    return jsonify({'Mean_HR': mean, 'Tachycardia': check_tachy(mean, age)})


def validate_user_json(json):
    '''Validates new user jsons

    :params json: JSON object from POST
    '''

    schema = {
        'type': 'object',
        'properties': {
            'user_email': {
                'type': 'string',
                'format': 'email'
            },
            'user_age': {
                'type': 'number'
            },
            'heart_rate': {
                'type': 'number'
            }
        },
        'required': ['user_email', 'heart_rate']
    }

    jsonschema.validate(json, schema,
                        format_checker=jsonschema.FormatChecker())


def validate_hr_post_json(json):
    '''Validates heart rate since JSONs

    :params json: JSON object from POST
    '''

    schema = {
        'type': 'object',
        'properties': {
            'user_email': {
                'type': 'string',
                'format': 'email'
            },
            'heart_rate_average_since': {
                'type': 'string',
                'pattern': '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}'
            }
        },
        'required': ['user_email', 'heart_rate_average_since']
    }

    jsonschema.validate(json, schema,
                        format_checker=jsonschema.FormatChecker())


def check_tachy(hr, age):
    '''Returns true or false for tachycardia depending on age and heartrate,
    according to https://en.wikipedia.org/wiki/Tachycardia

    :params hr: Heart rate
    :params age: Age of user
    '''

    thresh = 0

    if age <= 1:
        thresh = 159
    elif age <= 2:
        thresh = 151
    elif age <= 4:
        thresh = 137
    elif age <= 7:
        thresh = 133
    elif age <= 11:
        thresh = 130
    elif age <= 15:
        thresh = 119
    else:
        thresh = 100

    if hr > thresh:
        return True
    else:
        return False


def mean_hr(hr_list):
    '''Averages of list of HRs

    :params hr_list: List of heart rates'''

    return np.asscalar(np.mean(hr_list))


def hr_mean_since(hr_list, t_list, t_since_str):
    '''Average of list of HRs since time

    :params hr_list: List of heart rates
    :params t_list: List of timestamps (unix epoch times)
    :params t: Beginning time to start average (unix epoch time)
    :return mean: Mean HR since time t'''

    t_int_list = [dt.timestamp() for dt in t_list]
    since_dt = parse_time_str(t_since_str)
    t_int = since_dt.timestamp()
    selected_list = [hr_list[i] for (i, t_i) in
                     enumerate(t_int_list) if t_i >= t_int]
    mean = mean_hr(selected_list)
    return mean


def parse_time_str(t_str):
    '''Parse time string into datetime object

    :params t_str: Time string of format 2018-03-09 11:00:36.372339
    '''

    format_str = '%Y-%m-%d %H:%M:%S.%f'
    dt = datetime.datetime.strptime(t_str, format_str)
    return dt


def add_heart_rate(email, heart_rate, time):
    user = models.User.objects.raw({"_id": email}).first()
    user.heart_rate.append(heart_rate)
    user.heart_rate_times.append(time)
    user.save()


def create_user(email, age, heart_rate, time):
    u = models.User(email, age, [], [])
    u.heart_rate.append(heart_rate)
    u.heart_rate_times.append(time)
    u.save()


def print_user(email):
    user = models.User.objects.raw({"_id": email}).first()
    print(user.email)
    print(user.heart_rate)
    print(user.heart_rate_times)
