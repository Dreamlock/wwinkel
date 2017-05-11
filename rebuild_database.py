import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wwinkel.settings")
django.setup()
from django.core.management import call_command
from subprocess import call
from glob import glob

if True:
    print('deleting old db...')
    try:
        os.remove('db.sqlite3')
    except FileNotFoundError:
        print('no db.sqlite3 found')
    print('  done')

    print('deleting old migrations...')
    migration_files = (
        glob('./custom_users/migrations/*_auto_*.py') +
        glob('./dbwwinkel/migrations/0001_initial.py') +
        glob('./dbwwinkel/migrations/*_auto_*.py')
    )
    [os.remove(file) for file in migration_files]
    print('  done')

    print('generating new migrations...')
    call_command('makemigrations', 'custom_users')
    call_command('makemigrations')
    print('  done')

    print('executing migrations...')
    call_command('migrate')
    print('  done')

print('importing data from csv')
csv_files = [
    'Province',
    'JuridicalEntity',
    'organisationtyes',
    'knowfrom',
    'organiation_details',
    'questiontypes',
    'institution',
    'faculty',
    'education',
]

call(['python', 'script.py'] + ['./CSV/'+file+'.csv' for file in csv_files])
print('  done')
