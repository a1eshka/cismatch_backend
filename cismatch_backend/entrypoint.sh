#!/bin/sh

if [ "$DATABASE" = "postgres" ] 
then


    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done

    echo "The database is up and running :-D"
fi

# Собираем статические файлы
#echo "Собираем статические файлы..."
#python manage.py collectstatic --noinput

# Запускаем бота **только если контейнер — web**
if [ "$CONTAINER_ROLE" = "web" ]; then
    echo "🤖 Запускаем бота..."
    python /usr/src/cismatch_backend/steam_client.py &
fi

# Запускаем сервер с использованием Uvicorn
#echo "Запускаем сервер с Uvicorn..."
#uvicorn cismatch_backend.asgi:application --host 0.0.0.0 --port 8000

exec "$@"