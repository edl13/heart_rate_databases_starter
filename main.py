from pymodm import connect
import models
import datetime


def add_heart_rate(email, heart_rate):
    user = models.User.objects.raw({"_id": email}).first()
    user.heart_rate.append(heart_rate)
    user.heart_rate_times.append(datetime.datetime.now())
    user.save()


def create_user(email, age, heart_rate):
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
    create_user(email="edl13@duke.edu", age=21, heart_rate=60)
    add_heart_rate("edl13@duke.edu", 68)
    print_user("edl13@duke.edu")
