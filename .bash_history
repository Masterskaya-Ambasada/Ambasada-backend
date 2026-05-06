python backend/manage.py migrate
python backend/manage.py createsuperuser
python backend/manage.py showmigrations users
cd backend/locale
msguniq en/LC_MESSAGES/django.po -o en/LC_MESSAGES/django.po
msguniq sr_Latn/LC_MESSAGES/django.po -o sr_Latn/LC_MESSAGES/django.po
msguniq sr_Cyrl/LC_MESSAGES/django.po -o sr_Cyrl/LC_MESSAGES/django.po
msguniq ru/LC_MESSAGES/django.po -o ru/LC_MESSAGES/django.po
exit
