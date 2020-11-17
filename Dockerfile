FROM pypy:3

WORKDIR /usr/share/app

COPY . .

RUN pip install -r requirements.txt

CMD [ "uvicorn" "api.asgi:application" ]

EXPOSE 8000
