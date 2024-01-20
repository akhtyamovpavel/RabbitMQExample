FROM python:3.10

RUN mkdir /code
ADD requirements.txt /code/

RUN pip3 install -r /code/requirements.txt

EXPOSE 8080

COPY . /code/
WORKDIR /code
