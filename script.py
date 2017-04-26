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

#path to province.csv
with open(sys.argv[1]) as f:
    reader = csv.reader(f)
    for row in reader:
        if (row[0]=="idprovince"):
            pass
        else:
            obj, created = cmmodels.Province.objects.get_or_create(
            id=int(row[0])-1,
            province=str(row[1]),
            )
    f.close()
   
#path to JuridicalEntity.csv
with open(sys.argv[2]) as f:
    reader = csv.reader(f)
    for row in reader:
        obj, created = cmmodels.LegalEntity.objects.get_or_create(
            ID=row[0],
            entity=row[1],
            )
    f.close()

