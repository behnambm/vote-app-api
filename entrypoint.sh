#!/bin/sh

if [ $USE_ENTRYPOINT ] && [ $USE_ENTRYPOINT == "True" ]
then
	python manage.py flush --no-input
    python manage.py migrate 
    python add_trigger_function_sql.py
    python manage.py createsuperuser --email admin@local.com --username admin --no-input
fi

# check redis connection
python -c "import redis; print('Checking Redis connection...', redis.Redis('$(echo $REDIS_HOST)').ping())"

exec "$@"