FROM python

WORKDIR /usr/share/app

COPY . .

RUN pip install -r requirements-dev.txt; \
    alias manage="python manage.py";