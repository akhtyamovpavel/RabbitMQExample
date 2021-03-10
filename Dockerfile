FROM python:3.9.0

RUN mkdir /code
ADD requirements.txt /code/

RUN pip3 install -r /code/requirements.txt

EXPOSE 8080

COPY . /code/
WORKDIR /code
