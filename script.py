import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wwinkel.settings")
django.setup()
from custom_users import models as cmmodels
from dbwwinkel import models as dbmodels
import csv, sys


""" paths to csv files can be passed by commandline in following order:

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
    if cdate == '':
        return "0001-01-01 01:01"
    fields=cdate.split('/')
    day=fields[1]
    month=fields[0]
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

#import organisation types
with open(sys.argv[3]) as f:
    reader = csv.reader(f)
    for row in reader:
        if (row[0] == "idorganizationtype"):
            pass
        else:
            obj, created = cmmodels.OrganisationType.objects.update_or_create(id=row[0], type=row[1])
            obj.save()
    f.close()

#import knowfrom
with open(sys.argv[4]) as f:
    reader = csv.reader(f)
    for row in reader:
        if (row[0] == "idquestionknowfrom"):
            pass
        else:
            obj,created = cmmodels.KnowFrom.objects.update_or_create(id=row[0],knowfrom=row[1])
            obj.save()
    f.close()

#import organisation
with open(sys.argv[5]) as f:
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
                tp = cmmodels.OrganisationType.objects.get(id=1)
                kf = cmmodels.KnowFrom.objects.get(id=1)
                obj, created = cmmodels.Organisation.objects.get_or_create(
                    id=row[0],
                    name=row[2],
                    recognised_abbreviation=row[3],
                    legal_entity=le,
                    address=adr,
                    telephone=498119433,
                    fax=498119433,
                    website=row[12],
                    mail="info@test.be",
                    goal=row[14],
                    remarks=row[16],
                    know_from = kf,
                    creation_date=refactored_date,
                    active=row[17],
                    type=tp
                )
                obj.save()
            except:
                pass

    f.close()

#import question types
with open(sys.argv[6]) as f:
    reader = csv.reader(f)
    for row in reader:
        if (row[0] == "idquestioninvestigationtype"):
            pass
        else:
            try:
                obj, created = dbmodels.QuestionType.objects.update_or_create(id=row[0], type=row[1])
                obj.save()
            except:
                pass
    f.close()

#import institution
with open(sys.argv[7]) as f:
    reader = csv.reader(f)
    for row in reader:
        if (row[0] == "idschool"):
            pass
        else:
            try:
                prov = cmmodels.Province.objects.get(id=row[1])
                adr, created = cmmodels.Address.objects.update_or_create(
                    province=prov,
                    city=row[7],
                    postal_code=row[6],
                    street_name=row[2],
                    street_number=row[5],
                )
                adr.save()
                obj, created = dbmodels.Institution.objects.update_or_create(id=row[0], name=row[4], address=adr)
                obj.save()
            except:
                pass
    f.close()

#import faculty
with open(sys.argv[8]) as f:
    reader = csv.reader(f)
    for row in reader:
        if (row[0] == "idfaculty"):
            pass
        else:
            try:
                inst = dbmodels.Institution.objects.get(id=row[1])
                print(inst)
                obj, created = dbmodels.Faculty.objects.update_or_create(id=row[0], name=row[2])
                obj.save()
                obj2, created = dbmodels.FacultyOf.objects.update_or_create(faculty=obj, institution=inst)
                obj2.save()
                #print("faculty {0} added".format(obj))
            except:
                #print("faculty failure", sys.exc_info())
                pass
    f.close()

#import education
with open(sys.argv[9]) as f:
    reader = csv.reader(f)
    for row in reader:
        if (row[0] == "ideducation"):
            pass
        else:
            try:
                fac = dbmodels.Faculty.objects.get(id=row[2])
                obj, created = dbmodels.Education.objects.update_or_create(id=row[0], education=row[3])
                obj.save()
                #print("education {0} added".format(obj))
            except:
                #print("education failure", sys.exc_info())
                pass
    f.close()