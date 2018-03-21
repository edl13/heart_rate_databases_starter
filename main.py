import numpy as np
from pymodm import connect
import models
import datetime
from flask import Flask, jsonify, request
from pymodm.errors import DoesNotExist
app = Flask(__name__)

connect("mongodb://localhost:27017/heart_rate_app")


@app.route('/api/heart_rate', methods=['POST'])
def post_hr_data():
    '''Posts HR data to Mongo database. If user exists, appends HR and
    timestamp to respective list

    :params json: JSON string with email, name, heart rate, and timestamp'''
    json = request.get_json()
    email = json['email']

    response = ''

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
    json = request.get_json()
    email = json['email']
    user = models.User.objects.raw({'_id': email}).first()
    heart_rate_list = user.heart_rate
    time_list = user.heart_rate_times
    time_since = json['heart_rate_average_since']
    mean = hr_mean_since(heart_rate_list, time_list, time_since)
    return jsonify({'Mean_HR': mean})


def mean_hr(hr_list):
    '''Averages of list of HRs

    :params hr_list: List of heart rates'''

    return np.asscalar(np.mean(hr_list))


def hr_mean_since(hr_list, t_list, t):
    '''Average of list of HRs since time

    :params hr_list: List of heart rates
    :params t_list: List of timestamps (unix epoch times)
    :params t: Beginning time to start average (unix epoch time)
    :return mean: Mean HR since time t'''

    selected_list = [hr_list[i] for (i, t_i) in enumerate(t_list) if t >= t]
    mean = mean_hr(selected_list)
    return mean


def add_heart_rate(email, heart_rate, time):
    user = models.User.objects.raw({"_id": email}).first()
    user.heart_rate.append(heart_rate)
    time_str = time.timestamp()
    user.heart_rate_times.append(time_str)
    user.save()


def create_user(email, age, heart_rate, time):
    u = models.User(email, age, [], [])
    u.heart_rate.append(heart_rate)
    u.heart_rate_times.append(datetime.datetime.now())
    u.save()


def print_user(email):
    user = models.User.objects.raw({"_id": email}).first()
    print(user.email)
    print(user.heart_rate)
    print(user.heart_rate_times)


if __name__ == "__main__":
    connect("mongodb://localhost:27017/heart_rate_app")
    create_user(email="edl13@duke.edu", age=21, heart_rate=60,
                time=datetime.datetime.now())
    add_heart_rate("edl13@duke.edu", 68, datetime.datetime.now())
    print_user("edl13@duke.edu")
