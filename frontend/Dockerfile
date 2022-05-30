FROM python:3.8-slim
RUN apt-get update && apt-get install -y python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools && rm -rf /var/lib/apt/lists/*
WORKDIR /frontend
COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN groupadd -r uwsgi && useradd -r -g uwsgi uwsgi
COPY . .
RUN chown -R uwsgi:uwsgi /frontend
USER uwsgi
EXPOSE 5000
CMD ["uwsgi","--ini","frontend.ini"]
