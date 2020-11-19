FROM python

WORKDIR /usr/share/app

COPY . .

RUN pip install -r requirements-dev.txt; \
    ln -s ${PWD}/manage.py /usr/bin/manage;