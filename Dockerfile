FROM python:3.5
ENV LANG C.UTF-8

WORKDIR /app

ENV DBNAME cs494
ENV DBUSER minhtus
ENV DBHOST 172.17.0.1
ENV DBPASSWD foobar


RUN pip install --upgrade pip
ADD requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

ADD . /app

CMD ["python" ,"run_server.py"]
