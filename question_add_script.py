import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wwinkel.settings")
django.setup()
# from django.contrib.auth.models import Group, Permission
from custom_users.models import *
from dbwwinkel.models import *
import csv
import sys
# from .script import refactorDate


def refactor_date_time(cdate):
    if '/' not in cdate:
        return "0000-00-00 00:00"
    fields = cdate.split('/')
    day = fields[0]
    month = fields[1]
    year_time = fields[2].split(' ')
    year = year_time[0]
    hour = year_time[1].split(':')[0]
    minute = year_time[1].split(':')[1]
    refactored_date = "{0}-{1}-{2} {3}:{4}".format(year, month, day, hour, minute)
    return refactored_date


def refactor_date(cdate):
    if '/' not in cdate:
        return "0000-00-00"
    fields = cdate.split('/')
    day = fields[0]
    month = fields[1]
    year_time = fields[2].split(' ')
    year = year_time[0]
    refactored_date = "{0}-{1}-{2}".format(year, month, day)
    return refactored_date


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


def add_question_statuses():
    for i in range(len(State.STATE_SELECT)):
        obj = State(id=i + 1, state=i)
        obj.save()
add_question_statuses()


# read questions
with open(sys.argv[1], newline='') as f:
    reader = csv.reader(f)
    first_row = next(reader)
    name_dict = dict(zip(first_row, range(len(first_row))))

    def get_row(string):
        return row[name_dict[string]]


    for row in reader:
        try:
            print(get_row('datecreated'), get_row('answerwithintermtext'))
            obj = Question(
                id=get_row('idquestion'),
                question_text=get_row('question'),
                reason=get_row('resultuse'),
                purpose=get_row('questionkickoff'),
                own_contribution=get_row('costcontrib'),

                remarks=get_row('remarks'),
                internal_remarks=get_row('intakeremarks'),
                # how_know_WW=get_row(''),
                how_know_WW='',
                deadline=refactor_date(get_row('answerwithintermtext')),

                public=get_row('resultpublic'),

                creation_date=refactor_date_time(get_row('datecreated')),
                active=get_row('active'),
                state=State.objects.get(state=state_id_map(int(get_row('reg_idquestionregstatus')))),

                # region

                # organisation=Organisation.objects.get(id=get_row('organizationcontact_idorganizationcontact')),
                organisation=Organisation(id=0),

                # keyword
                # question_subject
                # study_field
            )
            obj.save()
        except ValueError as e:
            if '\'NULL\'' in str(e) or '\'\'' in str(e):
                pass
            else:
                pass
                # raise
