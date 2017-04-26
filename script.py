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
        organisation keywords
        
"""

def province_map(old_province_id):
    idmap = {
        1: 0,4:1,2:2,3:3,5:4,6:5

    }
    return idmap[old_province_id]

for i in range(0, 6):
    obj, created = cmmodels.Province.objects.get_or_create(id=(i + 1))
    obj.province = i
    obj.save()

raise 1
#path to province.csv
with open(sys.argv[1]) as f:
    reader = csv.reader(f)
    for i in range(0, 6):
        obj, created = cmmodels.Province.objects.get_or_create(id=(i + 1))
        obj.province = i
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


