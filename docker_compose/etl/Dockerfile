FROM python:3.10

WORKDIR /opt/etl

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .

RUN  pip install --upgrade pip && pip install -r requirements.txt

RUN apt-get update && apt-get -y dist-upgrade
RUN apt-get install -y netcat
ADD https://raw.githubusercontent.com/eficode/wait-for/v2.2.3/wait-for .
RUN chmod 777 ./wait-for

#CMD ["python", "load_data.py"]