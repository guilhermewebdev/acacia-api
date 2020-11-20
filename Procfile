release: python manage.py migrate
web: uvicorn api.asgi:application --port $PORT --host 0.0.0.0 --header Server:nosniff --header Via:DENY