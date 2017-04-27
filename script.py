import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wwinkel.settings")
django.setup()
from custom_users import models as cmmodels
from dbwwinkel import models as dbmodels
import csv, sys


""" paths to csv files can be passed by commandline in following order:
        province
        legal entity
        organisation
        questionstatus
        questiontypes
        question
        questionpertype
        
"""

def province_map(old_province_id):
    idmap = {
        '1': 0,
        '4': 1,
        '2': 2,
        '3': 3,
        '5': 4,
        '6': 5
    }
    return idmap[old_province_id]

def refactorDate(cdate):
    if len(cdate) < 14 or len(cdate) > 16:
        return "0001-01-01 01:01"
    fields=cdate.split('/')
    day=fields[0]
    month=fields[1]
    year_time=fields[2].split(' ')
    year=year_time[0]
    hour=year_time[1].split(':')[0]
    minute=year_time[1].split(':')[1]
    refactored_date = "{0}-{1}-{2} {3}:{4}".format(year,month,day,hour,minute)
    return refactored_date

def state_map(old_state_id):
    idmap={
        '1':0,
        '2':1,
        '3':8,
        '4':1,
        '5':2,
        '6':0,
        '7':4,
        '8':3,
        '9':8,
        '10':9,
        '11':5,
        '12':6,
        '13':7
    }
    return idmap[old_state_id]

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

def refactor_date_time(cdate):
    if '/' not in cdate:
        return "0001-01-01 01:01"
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
        return "0001-01-01"
    fields = cdate.split('/')
    day = fields[0]
    month = fields[1]
    year_time = fields[2].split(' ')
    year = year_time[0]
    refactored_date = "{0}-{1}-{2}".format(year, month, day)
    return refactored_date

#path to province.csv
with open(sys.argv[1]) as f:
    print(f)
    reader = csv.reader(f)
    for row in reader:
        if (row[0]=="idprovince"):
            pass
        else:
            new_id = province_map(row[0])
            obj = cmmodels.Province(id=row[0], province=new_id)
            obj.save()
    f.close()
    

#path to JuridicalEntity.csv
with open(sys.argv[2]) as f:
    reader = csv.reader(f)
    for row in reader:
        if (row[0]=="idjuridicalentity"):
            pass
        else:
            obj, created = cmmodels.LegalEntity.objects.update_or_create(
                id=row[0],
                )
            obj.entity=row[1]
            obj.save()
    f.close()

#import organisation
with open(sys.argv[3]) as f:
    reader = csv.reader(f)
    for row in reader:
        if (row[0] == "idorganization"):
            pass
        else:
            try:
                prov = cmmodels.Province.objects.get(id=row[9])
                adr,created = cmmodels.Address.objects.update_or_create(
                    province=prov,
                    city=row[8],
                    postal_code=row[7],
                    street_name=row[5],
                    street_number=row[6],
                )
                adr.save()
                cdate = row[18]
                refactored_date=refactorDate(cdate)
                le = cmmodels.LegalEntity.objects.get(id=row[4])
                obj,created = cmmodels.Organisation.objects.update_or_create(id=row[0],
                address=adr,
                legal_entity=le,
                active=row[17],
                creation_date=refactored_date,
                #fax=row[11],
                goal=row[14],
                name=row[2],
                recognised_abbreviation=row[3],
                remarks=row[16],
                telephone=498119433,
                #website=row[12],
                )
                obj.save()
            except:
                pass
    f.close()

#import questionstatus
with open(sys.argv[4]) as f:
    pass
    '''reader = csv.reader(f)
    for row in reader:
        if (row[0]=="idquestionregstatus"):
            pass
        else:
            try:
                print(row[0])
                obj = dbmodels.State(id=row[0],state=state_map(row[0]))
                print(row[1])
                obj.save()
            except:
                pass'''
    f.close()

#import questiontypes
with open(sys.argv[5]) as f:
    reader = csv.reader(f)
    for row in reader:
        if (row[0]=="idquestioninvestigationtype"):
            pass
        else:
            try:
                print(row[0])
                obj = dbmodels.QuestionSubject(id=row[0],subject=row[1])
                print(row[1])
                obj.save()
            except:
                pass
    f.close()

#import question
with open(sys.argv[6]) as f:
    reader = csv.reader(f)
    first_row = next(reader)
    name_dict = dict(zip(first_row, range(len(first_row))))

    def get_row(string):
        return row[name_dict[string]]


    for row in reader:
        try:
            print(get_row('datecreated'), get_row('answerwithintermtext'))
            obj = dbmodels.Question(
                id=row[0],
                question_text=row[3],
                reason=row[7],
                purpose=row[6],
                own_contribution=row[11],

                remarks=row[15],
                internal_remarks=row[17],
                # how_know_WW=get_row(''),
                how_know_WW='',
                deadline=refactor_date(row[9]),

                public=row[12],

                creation_date=refactorDate(row[24]),
                active=row[25],
                state=dbmodels.State.objects.get(state=state_id_map(int(row[20]))),

                # region

                # organisation=Organisation.objects.get(id=get_row('organizationcontact_idorganizationcontact')),
                organisation=dbmodels.Organisation.objects.get(id=33),

                # keyword
                # question_subject
                # study_field
            )
            obj.save()
        except: #ValueError as e:
            '''if '\'NULL\'' in str(e) or '\'\'' in str(e):
                pass
            else:'''
            pass
                # raise
#import questionpertype
