FROM python:3.6

WORKDIR /usr/share/app

COPY . .

RUN pip install -r requirements-dev.txt; \
    ln -s ${PWD}/manage.py /usr/bin/manage;