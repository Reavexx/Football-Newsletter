FROM python:alpine3.17

WORKDIR /usr/app/src

COPY ./src/* .

COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

CMD ["python3", "read.py"]