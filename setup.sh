#!/bin/bash

# Start Gunicorn
gunicorn news_reader.wsgi:application &

#Start Celery Worker
celery -A news_reader worker --pool=gevent  --concurrency=3 -l-Info &

# Start Celery Beat
celery -A news_reader beat --loglevel=info &

# Wait for all background processes
wait