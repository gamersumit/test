 echo "BUILD START"
 python3.9 -m pip install -r requirements.txt
 python3.9 manage.py migrate
 python3 manage.py collectstatic --noinput
 echo "BUILD END"