import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wwinkel.settings")
django.setup()
from custom_users import models as cmmodels
from dbwwinkel import models as dbmodels
import csv, sys, datetime
from django.core.exceptions import ObjectDoesNotExist

""" paths to csv files can be passed by commandline in following order:

"""

start_time = datetime.datetime.now()

organisation_id_dict = {}
organisation_user_id_dict = {}
manager_id_dict = {}
user_id_dict = {}


def add_organisation_id(old_id, new_id):
    organisation_id_dict[old_id] = new_id


def add_organisation_user_id(old_id, new_id):
    organisation_user_id_dict[old_id] = new_id


def add_manager_id(old_id, new_id):
    manager_id_dict[old_id] = new_id


def add_user_id(old_id, new_id):
    organisation_user_id_dict[old_id] = new_id


def get_new_organisation_id(old_id):
    return organisation_id_dict[old_id]


def get_new_organisation_user_id(old_id):
    return organisation_user_id_dict[old_id]


def get_new_manager_id(old_id):
    return manager_id_dict[old_id]


def get_new_user_id(old_id):
    return user_id_dict[old_id]


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


def refactorDeadline(cdate):
    try:
        if len(cdate) < 14 or len(cdate) > 16:
            return
        if cdate == '':
            return
        fields = cdate.split('/')
        day = fields[1]
        month = fields[0]
        year_time = fields[2].split(' ')
        year = year_time[0]
        refactored_date = "{0}-{1}-{2}".format(year, month, day)
        return refactored_date
    except:
        return


def refactorDate(cdate):
    try:
        if len(cdate) < 14 or len(cdate) > 16:
            return
        if cdate == '':
            return
        fields = cdate.split('/')
        day = fields[1]
        month = fields[0]
        year_time = fields[2].split(' ')
        year = year_time[0]
        hour = year_time[1].split(':')[0]
        minute = year_time[1].split(':')[1]
        refactored_date = "{0}-{1}-{2} {3}:{4}:00.000123".format(year, month, day, hour, minute)
        return refactored_date
    except:
        return


def refactorDate2(cdate):
    try:
        if len(cdate) < 14 or len(cdate) > 16:
            return
        if cdate == '':
            return
        fields = cdate.split('/')
        day = fields[1]
        month = fields[0]
        year_time = fields[2].split(' ')
        year = year_time[0]
        hour = year_time[1].split(':')[0]
        minute = year_time[1].split(':')[1]
        refactored_date = "{0}-{1}-{2}".format(year, month, day)
        return refactored_date
    except:
        return


def state_map(old_state_id):
    idmap = {
        '1': 0,
        '2': 1,
        '3': 8,
        '4': 1,
        '5': 1,
        '6': 0,
        '7': 3,
        '8': 4,
        '9': 8,
        '10': 9,
        '11': 5,
        '12': 6,
        '13': 7
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


# path to province.csv
with open(sys.argv[1], encoding='latin1') as f:
    print("importing provinces")
    print(f)
    reader = csv.reader(f)
    for row in reader:
        if (row[0] == "idprovince"):
            pass
        else:
            obj = cmmodels.Province(id=row[0], province=province_map(row[0]))
            obj.save()
    print("done")
    f.close()

print("creating regions")
for region in cmmodels.Region.REGION_SELECT:
    new_region, _ = cmmodels.Region.objects.update_or_create(
        region=region[0]
    )
    new_region.save()
print("done")

# path to JuridicalEntity.csv
with open(sys.argv[2], encoding='latin1') as f:
    print("importing legal entities")
    reader = csv.reader(f)
    for row in reader:
        if (row[0] == "idjuridicalentity"):
            pass
        else:
            obj, created = cmmodels.LegalEntity.objects.update_or_create(
                id=row[0],
            )
            obj.entity = row[1]
            obj.save()
    print("done")
    f.close()

# import organisation types
with open(sys.argv[3], encoding='latin1') as f:
    print("importing organizations types")
    reader = csv.reader(f)
    for row in reader:
        if (row[0] == "idorganizationtype"):
            pass
        else:
            obj, created = cmmodels.OrganisationType.objects.update_or_create(id=row[0], type=row[1])
            obj.save()
    print("done")
    f.close()

# import knowfrom
with open(sys.argv[4], encoding='latin1') as f:
    print("importing know froms")
    reader = csv.reader(f)
    for row in reader:
        if (row[0] == "idquestionknowfrom"):
            pass
        else:
            obj, created = cmmodels.KnowFrom.objects.update_or_create(id=row[0], knowfrom=row[1])
            obj.save()
    print("done")
    f.close()

# import organisation
with open(sys.argv[5], encoding='latin1') as f:
    print("importing organizations")
    reader = csv.reader(f)
    for row in reader:
        if (row[0] == "idorganization"):
            pass
        else:
            try:
                prov = cmmodels.Province.objects.get(id=province_map(row[9]))
                adr, created = cmmodels.Address.objects.get_or_create(
                    province=prov,
                    city=row[8],
                    postal_code=row[7],
                    street_name=row[5],
                    street_number=row[6],
                )
                adr.save()
                cdate = row[18]
                refactored_date = refactorDate(cdate)
                le = cmmodels.LegalEntity.objects.get(id=row[4])
                tp = cmmodels.OrganisationType.objects.get(id=1)
                kf = cmmodels.KnowFrom.objects.get(id=1)
                obj, created = cmmodels.Organisation.objects.get_or_create(
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
                    know_from=kf,
                    creation_date=refactored_date,
                    active=row[17],
                    type=tp
                )
                obj.save()
                add_organisation_id(int(row[0]), obj.id)
            except:
                # print(sys.exc_info())
                pass
    print(organisation_id_dict)
    print("done")
    f.close()

# import question types
with open(sys.argv[6], encoding='latin1') as f:
    print("importing question types")
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
    print("done")
    f.close()

# import institution
with open(sys.argv[7], encoding='latin1') as f:
    print("importing institutions")
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
                # print(sys.exc_info())
                pass
    print("done")
    f.close()

# import faculty
with open(sys.argv[8], encoding='latin1') as f:
    print("importing faculties")
    reader = csv.reader(f)
    for row in reader:
        if (row[0] == "idfaculty"):
            pass
        else:
            try:
                inst = dbmodels.Institution.objects.get(id=row[1])
                # print(inst)
                obj, created = dbmodels.Faculty.objects.update_or_create(id=row[0], name=row[2])
                obj.save()
                obj2, created = dbmodels.FacultyOf.objects.update_or_create(faculty=obj, institution=inst)
                obj2.save()
                # print("faculty {0} added".format(obj))
            except:
                # print("faculty failure", sys.exc_info())
                pass
    print("done")
    f.close()

# import education
with open(sys.argv[9], encoding='latin1') as f:
    print("importing educations")
    reader = csv.reader(f)
    for row in reader:
        if (row[0] == "ideducation"):
            pass
        else:
            try:
                fac = dbmodels.Faculty.objects.get(id=row[2])
                inst = dbmodels.Institution.objects.get(id=row[1])
                obj, created = dbmodels.Education.objects.update_or_create(id=row[0], education=row[3])
                obj.save()
                obj2 = dbmodels.FacultyOf.objects.get(faculty=fac, institution=inst)
                obj2.education.add(obj)
                obj2.save()
                # print("education {0} added".format(obj))
            except:
                # print("education failure", sys.exc_info())
                pass
    print("done")
    f.close()

# import students
with open(sys.argv[10], encoding='latin1') as f:
    print("importing students")
    reader = csv.reader(f)

    first_row = next(reader)
    name_dict = dict(zip(first_row, range(len(first_row))))  # dit leest header row in


    def get_row(string):
        return row[name_dict[string]]


    adr, created = cmmodels.Address.objects.get_or_create(
        province=cmmodels.Province.objects.get(id=1),
        city="Merksem",
        postal_code=2170,
        street_name="trammezandlei",
        street_number=122,
    )
    adr.save()
    for row in reader:
        try:
            if (get_row('studenteducation') != "NULL"):
                # print(get_row('studenteducation'))
                try:
                    ed = dbmodels.Education.objects.get(education=get_row('studenteducation'))
                    # print(ed)
                except:
                    ed = dbmodels.Education.objects.get(education='Rechten')
            if (get_row('studenteducation') == "NULL"):
                ed = dbmodels.Education.objects.get(education='Rechten')
                # print(ed)
            if (get_row('studentname') != "NULL"):
                sname = get_row('studentname')
                if sname != "":
                    sfname = sname.split(' ')[0]
                    slname = sname.split(' ')[1:]
            else:
                sfname = "Joske"
                slname = "Vemeulen"
            stud, created = dbmodels.Student.objects.update_or_create(
                first_name=sfname,
                last_name=slname,
                mobile=498119433,
                email="test@test.be",
                address=adr,
                education=ed
            )
            stud.save()
        except:
            # print(sys.exc_info())
            pass
    print("done")
    f.close()

# import question
with open(sys.argv[10], encoding='latin1') as f:
    # problems=open('questionproblems.txt', 'r+')
    print("importing questions")
    reader = csv.reader(f)

    first_row = next(reader)
    name_dict = dict(zip(first_row, range(len(first_row))))  # dit leest header row in


    def get_row(string):
        return row[name_dict[string]]


    adr, created = cmmodels.Address.objects.get_or_create(
        province=cmmodels.Province.objects.get(id=1),
        city="Merksem",
        postal_code=2170,
        street_name="trammezandlei",
        street_number=122,
    )
    adr.save()
    for row in reader:
        try:
            if (get_row('studenteducation') != "NULL"):
                try:
                    ed = dbmodels.Education.objects.get(education=get_row('studenteducation'))
                except:
                    ed = dbmodels.Education.objects.get(education='Rechten')
            if (get_row('studenteducation') == "NULL"):
                ed = dbmodels.Education.objects.get(education='Rechten')

            if (get_row('studentname') != "NULL"):
                sname = get_row('studentname')
                if sname != "":
                    sfname = sname.split(' ')[0]
                    slname = sname.split(' ')[1:]
            else:
                sfname = "Joske"
                slname = "Vemeulen"
            stud = dbmodels.Student.objects.get(
                first_name=sfname,
                last_name=slname,
                education=ed,
            )

            date = get_row('answerwithintermtext')
            rdate = refactorDeadline(date)
            date2 = get_row('datecreated')
            cdate = refactorDate(date2)
            print('org.id:', get_new_organisation_id(int(get_row('organization_idorganization'))), get_row('organization_idorganization'))
            org = dbmodels.Organisation.objects.get(
                id=get_new_organisation_id(int(get_row('organization_idorganization')))
            )
            compdate = refactorDate(get_row('dateregcompleted'))

            group, created = dbmodels.QuestionGroups.objects.update_or_create(id=get_row('idquestion'))
            group.save()

            obj, created = dbmodels.Question.objects.update_or_create(
                id=get_row('idquestion'),
                question_text=get_row('question'),
                reason=get_row('questionkickoff'),
                purpose=get_row('resultuse'),
                own_contribution=get_row('costcontrib'),
                remarks=get_row('remarks'),
                internal_remarks=get_row('intakeremarks'),
                deadline=rdate,
                public=int(get_row('resultpublic')),
                creation_date=cdate,
                active=int(get_row('active')),
                organisation=org,
                # institution=inst,
                student=stud,
                completion_date=compdate,
                # education=str(ed.id),
                state=int(state_map(get_row("reg_idquestionregstatus"))),
                question_group=group
            )
            # obj.save()

            if (get_row('school_idschool') != "NULL"):
                try:
                    if (int(get_row('school_idschool')) >= 12) and (int(get_row('school_idschool')) <= 16):
                        # inst = dbmodels.Institution.objects.get(id=int(get_row('school_idschool')))
                        inst = dbmodels.Institution.objects.get(id=int(get_row('school_idschool')))
                    else:
                        inst = dbmodels.Institution.objects.get(id=12)
                except:
                    inst = dbmodels.Institution.objects.get(id=12)
            else:
                inst = dbmodels.Institution.objects.get(id=12)

            obj.institution.add(inst)

            obj.education.add(ed)
            prov = inst.address.province
            prov_id = prov.id
            # print(prov_id)
            region_id = province_map(str(prov_id))
            # print(region_id)
            reg = cmmodels.Region.objects.get(region=region_id)
            # print(reg)
            obj.region.add(reg)
            obj.save()
        except ObjectDoesNotExist:
            pass
            # print(sys.exc_info(), 'question id:', obj.id)
        except:
            # problems.write(str((sys.exc_info(), ' ', get_row('idquestion'),' ', inst.address.province,' ', inst,' ', ed)))
            # problems.write("\n")
            #print(sys.exc_info())
            pass
    print("done")
    # problems.close()
    f.close()

# import keywords
with open(sys.argv[11], encoding='latin1') as f:
    print("importing keywords")
    reader = csv.reader(f)

    first_row = next(reader)
    name_dict = dict(zip(first_row, range(len(first_row))))  # dit leest header row in


    def get_row(string):
        return row[name_dict[string]]


    for row in reader:
        try:
            kw, created = cmmodels.Keyword.objects.get_or_create(
                id=int(get_row('idorganizationkeyword')),
                key_word=get_row('keywordname')
            )
            kw.save()
        except:
            pass
    print("done")
    f.close()

# add keywords to organizations
with open(sys.argv[12], encoding='latin1') as f:
    print("adding keywords to organisations")
    reader = csv.reader(f)

    first_row = next(reader)
    name_dict = dict(zip(first_row, range(len(first_row))))  # dit leest header row in


    def get_row(string):
        return row[name_dict[string]]


    for row in reader:
        try:
            org = cmmodels.Organisation.objects.get(
                id=get_new_organisation_id(int(get_row('organization_idorganization')))
            )
            kw = cmmodels.Keyword.objects.get(id=int(get_row('organizationkeyword_idorganizationkeyword')))
            org.keyword.add(kw)
            org.save()
        except:
            pass
    print("done")
    f.close()

# import promotors
with open(sys.argv[13], encoding='latin1') as f:
    print("importing promotors")
    reader = csv.reader(f)

    first_row = next(reader)
    name_dict = dict(zip(first_row, range(len(first_row))))  # dit leest header row in


    def get_row(string):
        return row[name_dict[string]]


    for row in reader:
        try:
            if (get_row('Promotor_Institution') == "VUB") or (get_row('Promotor_Institution') == "VUB Etterbeek") or (
                        get_row('Promotor_Institution') == "VUB Jette"):
                inst = dbmodels.Institution.objects.get(id=13)
            else:
                inst = dbmodels.Institution.objects.get(name=get_row('Promotor_Institution'))
            if (get_row('Promotor_Expertise') == "''"):
                exp = " "
            else:
                exp = get_row('Promotor_Expertise')
            adr = inst.address
            promotor, created = dbmodels.Promotor.objects.get_or_create(
                id=int(get_row('Promotor_ID')),
                address=adr,
                institution=inst,
                email="test@test.be",
                expertise=exp,
                first_name=get_row('Promotor_FirstName'),
                last_name=get_row('Promotor_LastName'),
                promo_class=get_row('Promotor_Class'),
                tel=498119433
            )
            promotor.save()
        except:
            # print(sys.exc_info())
            pass
    print("done")
    f.close()

# import users
with open(sys.argv[14], encoding='latin1') as f:
    print("importing users")
    reader = csv.reader(f)

    first_row = next(reader)
    name_dict = dict(zip(first_row, range(len(first_row))))  # dit leest header row in


    def get_row(string):
        return row[name_dict[string]]


    for row in reader:
        try:
            superuser = 0
            isstaff = 0
            if (int(get_row('UserRole_ID')) == 1):
                superuser = 1
                isstaff = 1
            if (int(get_row('UserRole_ID')) == 2):
                isstaff = 1
            usr, created = cmmodels.User.objects.update_or_create(
                first_name=get_row('User_Name'),
                email="{0}@{1}.be".format(get_row('User_Name'), "wwinkel"),
                is_superuser=superuser,
                is_staff=isstaff
            )
            usr.save()
            add_user_id(int(get_row('User_ID')), usr.id)
        except:
            # print(sys.exc_info())
            pass
    print("done")
    f.close()

# add education, faculty and institution to questions
with open(sys.argv[15], encoding='latin1') as f:
    print("add education, faculty and institution to questions")
    reader = csv.reader(f)

    first_row = next(reader)
    name_dict = dict(zip(first_row, range(len(first_row))))  # dit leest header row in


    def get_row(string):
        return row[name_dict[string]]


    for row in reader:
        try:
            quest = dbmodels.Question.objects.get(id=int(get_row('question_idquestion')))
            ed = dbmodels.Education.objects.get(id=int(get_row('education_ideducation')))

            facsinsts = dbmodels.FacultyOf.objects.get(education=ed)

            quest.faculty.add(facsinsts.faculty)
            quest.institution.add(facsinsts.institution)
            quest.save()
        except:
            # print(sys.exc_info())
            pass
    print("done")
    f.close()

# import logs
with open(sys.argv[16], encoding='latin1') as f:
    print("import logs")
    reader = csv.reader(f)

    first_row = next(reader)
    name_dict = dict(zip(first_row, range(len(first_row))))  # dit leest header row in


    def get_row(string):
        return row[name_dict[string]]


    for row in reader:
        try:
            log, created = dbmodels.Log.objects.get_or_create(id=int(get_row('question_idquestion')))
            rec, created = dbmodels.LogRecord.objects.get_or_create(
                id=int(get_row('idquestionlog')),
                description=get_row('description'),
                subject=get_row('event'),
                timestamp=refactorDate(get_row('datecreated'))
            )
            rec.save()
            log.record.add(rec)
            log.save()
        except:
            # print(sys.exc_info())
            pass
    print("done")
    f.close()

# import question institutions
with open(sys.argv[17], encoding='latin1') as f:
    print("import question institutions")
    reader = csv.reader(f)

    first_row = next(reader)
    name_dict = dict(zip(first_row, range(len(first_row))))  # dit leest header row in


    def get_row(string):
        return row[name_dict[string]]


    for row in reader:
        try:
            prov = cmmodels.Province.objects.get(id=get_row('province_idprovince'))
            adr, created = cmmodels.Address.objects.get_or_create(
                province=prov,
                city=get_row('city'),
                postal_code=int(get_row('postal')),
                street_name=get_row('street'),
                street_number=int(get_row('streetnumber')),
            )
            adr.save()
            questinst, created = cmmodels.QuestionInstitution.objects.update_or_create(
                id=int(get_row('idquestioninstitution')),
                address=adr,
                name=get_row('name')
            )
            questinst.save()
        except:
            print(sys.exc_info())
            pass
    print("done")
    f.close()

# import mediators
with open(sys.argv[18], encoding='latin1') as f:
    print("import mediators")
    reader = csv.reader(f)

    first_row = next(reader)
    name_dict = dict(zip(first_row, range(len(first_row))))  # dit leest header row in


    def get_row(string):
        return row[name_dict[string]]


    for row in reader:
        try:
            mediator, created = cmmodels.Mediator.objects.update_or_create(
                first_name=get_row('firstname'),
                last_name=get_row('lastname'),
                email="{0}.{1}@{2}.be".format(get_row('firstname'), get_row('idquestionmediator'), "wwinkel"),
                is_superuser=0,
                is_staff=1,
            )
            mediator.jobfunction = get_row('jobfunction')
            mediator.save()
            add_manager_id(int(get_row('idquestionmediator')), mediator.id)
        except:
            print(sys.exc_info())
            pass
    print("done")
    f.close()

end_time = datetime.datetime.now()
print(start_time)
print(end_time)
