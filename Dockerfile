FROM python:3.12.2-alpine3.19

ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app

WORKDIR $APP_HOME
COPY requirements.txt src ./

RUN apt-get update && apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/'        /etc/locale.gen \
    && sed -i -e 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen

ENV LANG pt_BR.UTF-8
ENV LC_ALL pt_BR.UTF-8

RUN pip install -r requirements.txt
RUN pip install gunicorn

CMD gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 app:server