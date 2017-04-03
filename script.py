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
        obj, created = LegalEntity.objects.get_or_create(
            ID=row[0],
            name=row[1],
            active=row[2],
            )
    f.close()
   
#path to JuridicalEntity.csv
with open(sys.argv[2]) as f:
    reader = csv.reader(f)
    for row in reader:
        obj, created = LegalEntity.objects.get_or_create(
            ID=row[0],
            entity=row[1],
            active=row[2],
            )
    f.close()
    
#path to organisation.csv
with open(sys.argv[3]) as f:
    reader = csv.reader(f)
    for row in reader:
        obj, created = Address.objects.get_or_create(
            street_name=row[],
            street_number=row[],
            postal_code=row[],
            city=row[],
            province=row[]
            )
        a = Address.objects.filter(street_name=row[], street_number=row[], postal_code=row[])
        print a
        """obj, created = Organisation.objects.get_or_create(
            ID=row[0],
            password=row[1],
            organisation_name=row[2],
            recognised_abbreviation=row[3],
            legal_entity=row[4],
            telephone=row[10],
            fax=row[11],
            website=row[12],
            goal=row[14],
            remarks=row[16],
            active=row[17],
            creationdate=row[18],
            email=row[19],
            
            address=
            )"""
    f.close()
        
#path to organisation_keywords.csv
with open(sys.argv[4]) as f:
    reader = csv.reader(f)
    for row in reader:
        obj, created = LegalEntity.objects.get_or_create(
            ID=row[0],
            keyword=row[1],
            active=row[2],
            )
    f.close()
    
#path to 
with open(sys.argv[5]) as f:
    reader = csv.reader(f)
    for row in reader:
        obj, created = LegalEntity.objects.get_or_create(
            ID=row[0],
            keyword=row[1],
            active=row[2],
            )
    f.close()