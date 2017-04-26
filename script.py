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
        question
        
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
        return "0000-00-00 00:00"
    fields=cdate.split('/')
    month=fields[0]
    day=fields[1]
    year_time=fields[2].split(' ')
    year=year_time[0]
    hour=year_time[1].split(':')[0]
    minute=year_time[1].split(':')[1]
    refactored_date = "{0}-{1}-{2} {3}:{4}".format(year,month,day,hour,minute)
    return refactored_date


#path to province.csv
with open(sys.argv[1]) as f:
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
            #telephone=12345+int(row[0]),
            #website=row[12],
            )
            obj.save()
    f.close()

#import question
