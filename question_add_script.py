import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wwinkel.settings")
django.setup()
# from django.contrib.auth.models import Group, Permission
from custom_users.models import *
from dbwwinkel.models import *
import csv
import sys


for i in range(1, len(State.STATE_SELECT)+1):
    print(i)
    obj, _ = State.objects.get_or_create(id=i)


def add_question_statuses():
    # add question statuses
    for i in range(len(State.STATE_SELECT)):
        print(i+1)
        obj, _ = State.objects.get_or_create(id=(i+1))
        print(i+1, obj)
        obj.state = i
        obj.save()
add_question_statuses()


def state_id_map(state_id):
    state_dict = {
        1: 0,
        2: 1,
        3: 8,
        4: 1,
        5: 1,
        6: 0,
        7: 3,
        8: 4,
        9: 8,
        10: 9,
        11: 5,
        12: 6,
        13: 7
    }
    return state_dict[state_id]
raise 1
# read questions
with open(sys.argv[0]) as f:
    reader = csv.reader(f)
    for row in reader:
        obj, _ = Question.objects.get_or_create(id=row[0])
        print(row[0], end=', ')

    for i in range(0, 6):
        obj, created = Province.objects.get_or_create(id=(i + 1))
        obj.province = i
        obj.save()
    f.close()