web: gunicorn news_reader.wsgi --log-file -
worker: celery -A news_reader worker --pool=gevent --loglevel=info
beat: celery -A news_reader beat --loglevel=info
