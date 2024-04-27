kill -9 $(ps aux | grep 'python3 manage.py runserver 0.0.0.0:8000' | awk '{print $2}')
python3 manage.py runserver 0.0.0.0:8000
